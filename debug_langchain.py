
import pkgutil
import langchain
import os

print(f"Langchain file: {langchain.__file__}")
print(f"Langchain path: {langchain.__path__}")

def find_retrieval_qa():
    import importlib
    
    # Try common locations
    candidates = [
        "langchain.chains.RetrievalQA",
        "langchain.chains.retrieval_qa.base.RetrievalQA",
        "langchain_community.chains.RetrievalQA",
        "langchain.chains.retrieval_qa.RetrievalQA"
    ]
    
    for candidate in candidates:
        try:
            module_name, class_name = candidate.rsplit('.', 1)
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"FOUND RetrievalQA at: {candidate}")
                return
        except ImportError:
            pass
        except Exception as e:
            print(f"Error checking {candidate}: {e}")

    print("RetrievalQA NOT FOUND in structure.")

    # List submodules of langchain
    print("\nSubmodules of langchain:")
    try:
        for importer, modname, ispkg in pkgutil.iter_modules(langchain.__path__):
            print(f" - {modname}")
    except Exception as e:
        print(f"Error listing modules: {e}")

if __name__ == "__main__":
    find_retrieval_qa()
