import os
import requests
import json
from typing import Dict, List, Optional, Tuple, Union
from dotenv import load_dotenv

load_dotenv()

class OverleafConnector:
    """Manages connection and operations with Overleaf's API."""
    
    def __init__(self, token: str = None):
        """Initialize Overleaf connector.
        
        Args:
            token: Overleaf API token. If None, will try to get from environment
        """
        self.token = token or os.getenv("OVERLEAF_TOKEN")
        if not self.token:
            raise ValueError("Overleaf API token not provided and not found in environment")
            
        self.api_base_url = "https://api.overleaf.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def create_project(self, name: str, description: str = "") -> Tuple[bool, Union[str, Dict]]:
        """Create a new Overleaf project.
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            (success, result) tuple. If success is True, result is the project info dict.
            If False, result is an error message.
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/projects",
                headers=self.headers,
                json={"name": name, "description": description}
            )
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            return False, f"Error creating project: {str(e)}"
            
    def get_projects(self) -> Tuple[bool, Union[List[Dict], str]]:
        """Get all Overleaf projects for the current user.
        
        Returns:
            (success, result) tuple. If success is True, result is list of projects.
            If False, result is an error message.
        """
        try:
            response = requests.get(
                f"{self.api_base_url}/projects",
                headers=self.headers
            )
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            return False, f"Error getting projects: {str(e)}"
            
    def upload_file(self, project_id: str, file_path: str, file_name: str = None) -> Tuple[bool, str]:
        """Upload a file to an Overleaf project.
        
        Args:
            project_id: Overleaf project ID
            file_path: Path to local file
            file_name: Name to use in Overleaf (defaults to basename of file_path)
            
        Returns:
            (success, message) tuple
        """
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
            
        if file_name is None:
            file_name = os.path.basename(file_path)
            
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            # First create the file entity in the project
            file_headers = self.headers.copy()
            file_headers["Content-Type"] = "application/json" 
            
            response = requests.post(
                f"{self.api_base_url}/projects/{project_id}/files",
                headers=file_headers,
                json={"name": file_name}
            )
            response.raise_for_status()
            file_info = response.json()
            file_id = file_info.get("_id")
            
            if not file_id:
                return False, "File creation response did not include file ID"
                
            # Now upload the file content
            content_headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "text/plain" 
            }
            
            response = requests.put(
                f"{self.api_base_url}/projects/{project_id}/files/{file_id}",
                headers=content_headers,
                data=file_content
            )
            response.raise_for_status()
            
            return True, f"File {file_name} uploaded successfully to project {project_id}"
        except requests.exceptions.RequestException as e:
            return False, f"Error uploading file: {str(e)}"
            
    def upload_content(self, project_id: str, content: str, file_name: str) -> Tuple[bool, str]:
        """Upload content as a file to an Overleaf project.
        
        Args:
            project_id: Overleaf project ID
            content: String content to upload
            file_name: Name of the file to create
            
        Returns:
            (success, message) tuple
        """
        try:
            # First create the file entity in the project
            file_headers = self.headers.copy()
            
            response = requests.post(
                f"{self.api_base_url}/projects/{project_id}/files",
                headers=file_headers,
                json={"name": file_name}
            )
            response.raise_for_status()
            file_info = response.json()
            file_id = file_info.get("_id")
            
            if not file_id:
                return False, "File creation response did not include file ID"
                
            # Now upload the content
            content_headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "text/plain" 
            }
            
            response = requests.put(
                f"{self.api_base_url}/projects/{project_id}/files/{file_id}",
                headers=content_headers,
                data=content
            )
            response.raise_for_status()
            
            return True, f"Content uploaded successfully as {file_name} to project {project_id}"
        except requests.exceptions.RequestException as e:
            return False, f"Error uploading content: {str(e)}"
            
    def share_project(self, project_id: str, email: str, privilege: str = "readAndWrite") -> Tuple[bool, str]:
        """Share a project with another user.
        
        Args:
            project_id: Overleaf project ID
            email: Email of user to share with
            privilege: Access level (readOnly, readAndWrite, owner)
            
        Returns:
            (success, message) tuple
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/projects/{project_id}/invites",
                headers=self.headers,
                json={"email": email, "privileges": privilege}
            )
            response.raise_for_status()
            
            return True, f"Project {project_id} shared with {email} ({privilege})"
        except requests.exceptions.RequestException as e:
            return False, f"Error sharing project: {str(e)}"
            
    def get_project_url(self, project_id: str) -> str:
        """Get the URL to access a project on Overleaf.
        
        Args:
            project_id: Overleaf project ID
            
        Returns:
            Overleaf project URL
        """
        return f"https://www.overleaf.com/project/{project_id}"
        
    def create_resume_project(self, latex_content: str, project_name: str) -> Tuple[bool, str]:
        """Create a new project specifically for a resume.
        
        Args:
            latex_content: LaTeX content for the resume
            project_name: Name for the Overleaf project
            
        Returns:
            (success, result) tuple. If success is True, result is the project URL.
            If False, result is an error message.
        """
        # Create the project
        success, result = self.create_project(
            name=project_name,
            description="Resume created with AI Resume Optimization Tool"
        )
        
        if not success:
            return False, result
            
        project_id = result.get("id")
        if not project_id:
            return False, "Project creation response did not include project ID"
            
        # Upload the main LaTeX file
        success, message = self.upload_content(
            project_id=project_id,
            content=latex_content,
            file_name="resume.tex"
        )
        
        if not success:
            return False, message
            
        # Return the project URL
        return True, self.get_project_url(project_id)
