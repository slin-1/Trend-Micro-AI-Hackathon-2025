# RAG (Retrieval-Augmented Generation) system for Linux-to-Windows API conversion knowledge

import os
import chromadb
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinuxWindowsRAGSystem:
    """
    RAG system specifically designed for Linux-to-Windows API conversion knowledge.
    Uses ChromaDB for vector storage and simple text matching for demo purposes.

    This system stores knowledge about:
    - Linux system calls and their Windows equivalents
    - Code conversion patterns
    - Platform-specific implementation details
    - Common pitfalls and solutions
    """

    def __init__(self, db_path: str = None, collection_name: str = "linux_windows_conversion"):
        self.db_path = db_path or os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        self.collection_name = collection_name

        # Ensure database directory exists
        Path(self.db_path).mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.db_path)

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"✅ Loaded existing collection '{self.collection_name}'")
        except Exception:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Linux to Windows API conversion knowledge base"}
            )
            print(f"✅ Created new collection '{self.collection_name}'")
            # Populate with initial knowledge
            self._populate_initial_knowledge()

    def _populate_initial_knowledge(self):
        """Populate the knowledge base with initial Linux-to-Windows conversion knowledge"""
        initial_knowledge = [
            {
                "id": "file_operations_1",
                "content": "Linux open() system call converts to Windows CreateFile() API. Linux: int fd = open(filename, O_RDONLY); Windows: HANDLE hFile = CreateFile(filename, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);",
                "category": "file_operations",
                "linux_api": "open()",
                "windows_api": "CreateFile()"
            },
            {
                "id": "file_operations_2",
                "content": "Linux read() system call converts to Windows ReadFile() API. Linux: ssize_t bytes = read(fd, buffer, size); Windows: BOOL result = ReadFile(hFile, buffer, size, &bytesRead, NULL);",
                "category": "file_operations",
                "linux_api": "read()",
                "windows_api": "ReadFile()"
            },
            {
                "id": "file_operations_3",
                "content": "Linux write() system call converts to Windows WriteFile() API. Linux: ssize_t bytes = write(fd, buffer, size); Windows: BOOL result = WriteFile(hFile, buffer, size, &bytesWritten, NULL);",
                "category": "file_operations",
                "linux_api": "write()",
                "windows_api": "WriteFile()"
            },
            {
                "id": "file_operations_4",
                "content": "Linux close() system call converts to Windows CloseHandle() API. Linux: int result = close(fd); Windows: BOOL result = CloseHandle(hFile);",
                "category": "file_operations",
                "linux_api": "close()",
                "windows_api": "CloseHandle()"
            },
            {
                "id": "process_management_1",
                "content": "Linux fork() system call has no direct Windows equivalent. Use CreateProcess() instead. Linux: pid_t pid = fork(); Windows: BOOL result = CreateProcess(NULL, commandLine, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi);",
                "category": "process_management",
                "linux_api": "fork()",
                "windows_api": "CreateProcess()"
            },
            {
                "id": "threading_1",
                "content": "Linux pthread_create() converts to Windows CreateThread() or _beginthreadex(). Linux: pthread_create(&thread, NULL, thread_func, arg); Windows: HANDLE hThread = CreateThread(NULL, 0, thread_func, arg, 0, &threadId);",
                "category": "threading",
                "linux_api": "pthread_create()",
                "windows_api": "CreateThread()"
            }
        ]

        # Add documents to collection (without embeddings for simplicity)
        documents = [item["content"] for item in initial_knowledge]
        metadatas = [{k: v for k, v in item.items() if k != "content"} for item in initial_knowledge]
        ids = [item["id"] for item in initial_knowledge]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"✅ Populated knowledge base with {len(initial_knowledge)} initial conversion examples")

    def query_knowledge(self, query: str, top_k: int = 5, category_filter: str = None) -> List[Dict[str, Any]]:
        """Query the knowledge base for relevant information"""
        try:
            # Simple query using ChromaDB's built-in similarity
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"category": category_filter} if category_filter else None
            )

            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "similarity_score": 1 - results['distances'][0][i] if results['distances'] else 0.5
                })

            return formatted_results

        except Exception as e:
            print(f"❌ Error querying knowledge: {str(e)}")
            # Return empty results on error
            return []

    def get_conversion_suggestions(self, linux_code: str, context: str = "") -> List[Dict[str, Any]]:
        """Get Windows conversion suggestions for Linux code"""
        # Create a comprehensive query
        query = f"Convert Linux code to Windows: {linux_code}"
        if context:
            query += f" Context: {context}"

        # Query knowledge base
        results = self.query_knowledge(query, top_k=3)

        # Enhance results with specific suggestions
        suggestions = []
        for result in results:
            suggestion = {
                "linux_api": result['metadata'].get('linux_api', 'Unknown'),
                "windows_api": result['metadata'].get('windows_api', 'Unknown'),
                "category": result['metadata'].get('category', 'general'),
                "conversion_example": result['content'],
                "confidence": result['similarity_score'],
                "source_id": result['id']
            }
            suggestions.append(suggestion)

        return suggestions

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base collection"""
        try:
            collection_data = self.collection.get()

            # Count by category
            categories = {}
            for metadata in collection_data['metadatas']:
                category = metadata.get('category', 'uncategorized')
                categories[category] = categories.get(category, 0) + 1

            return {
                "total_documents": len(collection_data['ids']),
                "categories": categories,
                "collection_name": self.collection_name,
                "db_path": self.db_path
            }

        except Exception as e:
            print(f"❌ Error getting collection stats: {str(e)}")
            return {"error": str(e)}

# Global RAG system instance - initialized safely
try:
    rag_system = LinuxWindowsRAGSystem()
except Exception as e:
    print(f"❌ Warning: Could not initialize RAG system: {str(e)}")
    # Create a dummy RAG system for testing
    class DummyRAGSystem:
        def query_knowledge(self, query, top_k=5, category_filter=None):
            return []
        def get_conversion_suggestions(self, linux_code, context=""):
            return []
        def get_collection_stats(self):
            return {"total_documents": 0, "categories": {}, "error": "RAG system not initialized"}

    rag_system = DummyRAGSystem()
