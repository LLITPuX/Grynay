import sys
from falkordb import FalkorDB

def main():
    try:
        db = FalkorDB(host='falkordb', port=6379)
        graph = db.select_graph('Grynya')
    except Exception as e:
        print(f"Error connecting: {e}")
        return

    q_entities = """
    MATCH (e:Entity)
    RETURN toLower(e.name) as l_name, collect(e.id) as ids
    """
    res_entities = graph.query(q_entities)
    duplicates = [r for r in res_entities.result_set if len(r[1]) > 1]
    
    if not duplicates:
        print("No duplicate entities found.")
        return

    for name, ids in duplicates:
        primary_id = ids[0]
        redundant_ids = ids[1:]
        
        print(f"Merging '{name}' into Primary [{primary_id}] from {redundant_ids}")
        for r_id in redundant_ids:
            # Reconnect incoming relations
            q_find_in = f"MATCH (source)-[rel]->(redundant:Entity {{id: '{r_id}'}}) RETURN source.id, type(rel)"
            try:
                res_in = graph.query(q_find_in)
                for record in res_in.result_set:
                    s_id, r_type = record[0], record[1]
                    graph.query(f"MATCH (s {{id: '{s_id}'}}), (p:Entity {{id: '{primary_id}'}}) MERGE (s)-[:{r_type}]->(p)")
            except Exception as e:
                print(f"  Error mapping incoming relations for {r_id}: {e}")

            # Reconnect outgoing relations
            q_find_out = f"MATCH (redundant:Entity {{id: '{r_id}'}})-[rel]->(target) RETURN target.id, type(rel)"
            try:
                res_out = graph.query(q_find_out)
                for record in res_out.result_set:
                    t_id, r_type = record[0], record[1]
                    if t_id is not None:
                        graph.query(f"MATCH (p:Entity {{id: '{primary_id}'}}), (t {{id: '{t_id}'}}) MERGE (p)-[:{r_type}]->(t)")
            except Exception as e:
                print(f"  Error mapping outgoing relations for {r_id}: {e}")

            # Delete redundant node
            try:
                graph.query(f"MATCH (redundant:Entity {{id: '{r_id}'}}) OPTIONAL MATCH (redundant)-[r]-() DELETE r, redundant")
                print(f"  Merged and deleted {r_id}")
            except Exception as e:
                print(f"  Error deleting node {r_id}: {e}")

    print("Entity Deduplication Complete.")

if __name__ == "__main__":
    main()
