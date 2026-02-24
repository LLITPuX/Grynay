import sys
from falkordb import FalkorDB

def escape_str(val):
    return str(val).replace("'", "\\'").replace('"', '\\"')

def main():
    try:
        db = FalkorDB(host='falkordb', port=6379)
        graph = db.select_graph('Grynya')
    except Exception as e:
        print(f"Error connecting: {e}")
        return

    print("Phase 1: Finding Orphan Responses")
    res = graph.query("MATCH (r:Response) WHERE NOT (()-[:ANALYZES]->(r)) RETURN r.id, r.name")
    orphans = [record[0] for record in res.result_set]
    print(f"Found {len(orphans)} orphan responses: {orphans}")

    for r_id in orphans:
        print(f"\nProcessing {r_id}...")
        a_id = f"ana_migrated_{r_id}" 
        
        # 1. Create Analysis and link to Response
        q_create = f"""
        MATCH (r:Response {{id: '{r_id}'}})
        MERGE (a:Analysis {{id: '{a_id}'}})
        SET a.name = 'Відновлений Аналіз для ' + '{r_id}',
            a.type = 'response_analysis',
            a.verdict = 'recovered_historical',
            a.rules_used = 'migration_script',
            a.lessons = 'Відновлено скриптом міграції',
            a.errors = ''
        MERGE (a)-[:ANALYZES]->(r)
        """
        graph.query(q_create)
        
        # 2. Link to Session
        q_session = f"""
        MATCH (r:Response {{id: '{r_id}'}})-[:PART_OF]->(s:Session), (a:Analysis {{id: '{a_id}'}})
        MERGE (a)-[:PART_OF]->(s)
        """
        graph.query(q_session)

        # 3. Fix NEXT chain
        # Check if Response had a NEXT relation
        q_check_next = f"MATCH (r:Response {{id: '{r_id}'}})-[nxt:NEXT]->(nxtNode) RETURN nxtNode.id"
        res_next = graph.query(q_check_next)
        
        if res_next.result_set:
            nxt_id = res_next.result_set[0][0]
            print(f"  Response has NEXT relation to {nxt_id}. Rewiring...")
            q_rewire = f"""
            MATCH (r:Response {{id: '{r_id}'}})-[nxt:NEXT]->(nxtNode {{id: '{nxt_id}'}}), (a:Analysis {{id: '{a_id}'}})
            DELETE nxt
            MERGE (r)-[:NEXT]->(a)
            MERGE (a)-[:NEXT]->(nxtNode)
            """
            graph.query(q_rewire)
        else:
            print("  Response is at the end of the chain. Appending...")
            q_append = f"""
            MATCH (r:Response {{id: '{r_id}'}}), (a:Analysis {{id: '{a_id}'}})
            MERGE (r)-[:NEXT]->(a)
            """
            graph.query(q_append)

    print("\nPhase 4: Fixing LAST_EVENT pointers")
    # Find sessions whose LAST_EVENT is not Analysis
    q_bad_le = """
    MATCH (s:Session)-[le:LAST_EVENT]->(l)
    WHERE NOT l:Analysis
    RETURN s.id, l.id, labels(l)[0]
    """
    res_bad_le = graph.query(q_bad_le)
    bad_sessions = res_bad_le.result_set
    print(f"Found {len(bad_sessions)} sessions with invalid LAST_EVENT: {bad_sessions}")

    for record in bad_sessions:
        s_id = record[0]
        # Find the end of the chain from the session
        # Use a path match where the end node has no outgoing NEXT
        q_end = f"""
        MATCH (s:Session {{id: '{s_id}'}})-[:NEXT*]->(endNode)
        WHERE NOT (endNode)-[:NEXT]->()
        RETURN endNode.id
        """
        try:
            res_end = graph.query(q_end)
            if res_end.result_set:
                end_id = res_end.result_set[0][0]
                print(f"Updating {s_id} LAST_EVENT to {end_id}")
                q_update_le = f"""
                MATCH (s:Session {{id: '{s_id}'}})-[le:LAST_EVENT]->(), (endNode {{id: '{end_id}'}})
                DELETE le
                MERGE (s)-[:LAST_EVENT]->(endNode)
                """
                graph.query(q_update_le)
            else:
                print(f"Could not find end of NEXT chain for session {s_id}")
        except Exception as e:
            print(f"Error querying NEXT chain for {s_id}: {e}")

    print("\nPhase 5: Entity Audit")
    q_entities = """
    MATCH (e:Entity)
    RETURN toLower(e.name) as l_name, collect(e.id) as ids
    """
    res_entities = graph.query(q_entities)
    duplicates = [r for r in res_entities.result_set if len(r[1]) > 1]
    
    if duplicates:
        print(f"Found {len(duplicates)} duplicated entity names:")
        for name, ids in duplicates:
            print(f" - {name}: {ids}")
    else:
        print("No duplicate entity names found.")

    print("\nMigration Script Finished.")

if __name__ == "__main__":
    main()
