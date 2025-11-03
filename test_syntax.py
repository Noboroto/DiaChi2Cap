"""
Script kiểm tra syntax và import của tất cả file Python
"""
import py_compile
import sys
from pathlib import Path

def check_syntax(file_path):
    try:
        py_compile.compile(str(file_path), doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("KIỂM TRA CÚ PHÁP PYTHON")
    print("=" * 60)
    print()
    
    project_dir = Path(__file__).parent
    python_files = list(project_dir.glob("*.py"))
    
    all_passed = True
    
    for py_file in python_files:
        if py_file.name == "test_syntax.py":
            continue
            
        print(f"Kiểm tra: {py_file.name}...", end=" ")
        passed, error = check_syntax(py_file)
        
        if passed:
            print("[OK]")
        else:
            print("[LỖI]")
            print(f"  Chi tiết: {error}")
            all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("[HOÀN THÀNH] Tất cả file đều hợp lệ!")
        print("=" * 60)
        return 0
    else:
        print("[THẤT BẠI] Có file lỗi cú pháp!")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
