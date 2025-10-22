import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def setup_git_repo():
    """Initialize git repository and prepare for GitHub push."""
    print("Setting up git repository for transKriptor...")
    
    # Check if git is available
    returncode, _, _ = run_command("git --version")
    if returncode != 0:
        print("Error: Git is not installed or not in PATH")
        return False
    
    # Initialize git repository if not already initialized
    returncode, stdout, stderr = run_command("git init")
    if returncode != 0:
        print(f"Error initializing git: {stderr}")
        return False
    else:
        print("Git repository initialized")
    
    # Check if remote origin already exists
    returncode, stdout, stderr = run_command("git remote get-url origin")
    if returncode == 0:
        print(f"Remote origin already set to: {stdout.strip()}")
        change_remote = input("Do you want to change the remote origin? (y/N): ")
        if change_remote.lower() != 'y':
            print("Keeping existing remote origin")
        else:
            # Remove existing origin
            run_command("git remote remove origin")
            print("Removed existing origin")
    elif "No such file" in stderr or "not found" in stderr.lower():
        print("No remote origin set yet")
    else:
        print(f"Error checking remote: {stderr}")
    
    # Add remote origin if not set
    returncode, stdout, stderr = run_command("git remote get-url origin")
    if returncode != 0:
        remote_url = "https://github.com/ElishaPervez/transKriptor.git"
        returncode, stdout, stderr = run_command(f"git remote add origin {remote_url}")
        if returncode == 0:
            print(f"Added remote origin: {remote_url}")
        else:
            print(f"Error adding remote: {stderr}")
            return False
    
    # Add all files
    returncode, stdout, stderr = run_command("git add .")
    if returncode == 0:
        print("Added all files to staging")
    else:
        print(f"Error adding files: {stderr}")
        return False
    
    # Check git status
    returncode, stdout, stderr = run_command("git status --porcelain")
    if stdout.strip():
        print("\nFiles to be committed:")
        print(stdout)
    else:
        print("No files to commit")
        return False
    
    # Create initial commit
    commit_msg = "Initial commit: Whisper Transcription Assistant with RTX 50 series support"
    returncode, stdout, stderr = run_command(f'git commit -m "{commit_msg}"')
    if returncode == 0:
        print(f"Created initial commit: {commit_msg}")
    else:
        print(f"Error creating commit: {stderr}")
        return False
    
    print("\nRepository setup complete!")
    print("To push to GitHub, run:")
    print("  git push -u origin main")
    print("\nNote: You may need to create the repository on GitHub first if it doesn't exist.")
    
    return True

if __name__ == "__main__":
    setup_git_repo()