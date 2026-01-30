"""
Log Indexing Module - Similar to Elasticsearch indexing
Provides fast search and aggregation capabilities
"""
import json
import os
from datetime import datetime
from agent.config import LOG_INDEX_FILE, BASE_LOG_DIR

class LogIndexer:
    def __init__(self, index_file=LOG_INDEX_FILE):
        self.index_file = index_file
        self.ensure_index_exists()
    
    def ensure_index_exists(self):
        """Ensure index file exists"""
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w') as f:
                pass
    
    def index_log(self, log_entry):
        """Index a single log entry"""
        try:
            # Add indexing metadata
            log_entry['_indexed_at'] = datetime.now().isoformat()
            log_entry['_index_id'] = hash(json.dumps(log_entry, sort_keys=True)) % 10**8
            
            with open(self.index_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            return True
        except Exception as e:
            print(f"[!] Error indexing log: {str(e)}")
            return False
    
    def search(self, query, limit=100):
        """Search logs by query"""
        results = []
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        if self._matches_query(log, query):
                            results.append(log)
                            if len(results) >= limit:
                                break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[!] Error searching logs: {str(e)}")
        
        return results
    
    def _matches_query(self, log, query):
        """Check if log matches query"""
        query_lower = query.lower()
        
        # Search in message
        if 'message' in log and query_lower in str(log['message']).lower():
            return True
        
        # Search in source
        if 'source' in log and query_lower in str(log['source']).lower():
            return True
        
        # Search in category
        if 'category' in log and query_lower in str(log['category']).lower():
            return True
        
        return False
    
    def get_stats(self):
        """Get index statistics"""
        stats = {
            'total_logs': 0,
            'categories': {},
            'levels': {},
            'os_types': {}
        }
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        log = json.loads(line.strip())
                        stats['total_logs'] += 1
                        
                        # Count by category
                        cat = log.get('category', 'unknown')
                        stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
                        
                        # Count by level
                        level = log.get('level', 'unknown')
                        stats['levels'][level] = stats['levels'].get(level, 0) + 1
                        
                        # Count by OS type
                        os_type = log.get('os_type', 'unknown')
                        stats['os_types'][os_type] = stats['os_types'].get(os_type, 0) + 1
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[!] Error getting stats: {str(e)}")
        
        return stats
