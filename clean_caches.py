import os
import shutil
import subprocess

def clean_project():
    print("🧹 Starting project size optimization and cache purge...")
    
    # 1. Clean Python __pycache__ folders
    pycache_count = 0
    pyc_count = 0
    for root, dirs, files in os.walk("."):
        # Skip node_modules to avoid scanning millions of files
        if "node_modules" in dirs:
            dirs.remove("node_modules")
        if ".git" in dirs:
            dirs.remove(".git")
            
        for d in list(dirs):
            if d == "__pycache__":
                full_path = os.path.join(root, d)
                try:
                    shutil.rmtree(full_path)
                    print(f"🗑️ Deleted python cache: {full_path}")
                    pycache_count += 1
                except Exception as e:
                    print(f"⚠️ Could not delete {full_path}: {e}")
                    
        for f in files:
            if f.endswith(".pyc") or f.endswith(".pyo"):
                full_path = os.path.join(root, f)
                try:
                    os.remove(full_path)
                    pyc_count += 1
                except Exception as e:
                    print(f"⚠️ Could not delete file {full_path}: {e}")

    print(f"✅ Removed {pycache_count} '__pycache__' directories and {pyc_count} '.pyc' files.")

    # 2. Clean Vite's bundler cache in frontend/node_modules/.vite
    vite_cache_path = os.path.join("frontend", "node_modules", ".vite")
    if os.path.exists(vite_cache_path):
        try:
            shutil.rmtree(vite_cache_path)
            print(f"🗑️ Deleted Vite dependency pre-bundler cache: {vite_cache_path}")
            print("💡 Note: Vite will automatically rebuild this cache on the next 'npm run dev'.")
        except Exception as e:
            print(f"⚠️ Could not delete {vite_cache_path}: {e}")
    else:
        print("ℹ️ Vite pre-bundler cache folder (.vite) not found or already clean.")

    # 3. Clean local logs if needed (but preserve the prediction audit log folder structure)
    log_dir = "logs"
    if os.path.exists(log_dir):
        print(f"ℹ️ Found log folder: {log_dir}")
        # We keep the logs folder, but we can compress or clean old logs if desired.

    # 4. Git garbage collection and aggressive compression
    if os.path.exists(".git"):
        print("📦 Running Git Garbage Collection to compress repo database...")
        try:
            subprocess.run(["git", "gc", "--prune=now", "--aggressive"], check=True)
            print("✅ Git repository compressed successfully.")
        except Exception as e:
            print(f"⚠️ Git compression skipped (make sure Git is installed and not in use): {e}")

    print("\n🎉 Project optimization complete!")

if __name__ == "__main__":
    clean_project()
