from pathlib import Path

class FileSystemWriter:
    """Handles writing files to the filesystem."""

    def __init__(self, output_dir):
        self.output = Path(output_dir)

    def write_file(self, relative_path, content):
        """Write content to a file relative to output directory."""
        file_path = self.output / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    def append_to_file(self, relative_path, content):
        """Append content to a file relative to output directory."""
        file_path = self.output / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not file_path.exists():
            file_path.write_text(content)
        else:
            with open(file_path, 'a') as f:
                f.write(content)

    def create_directory(self, relative_path):
        """Create a directory relative to output directory."""
        dir_path = self.output / relative_path
        dir_path.mkdir(parents=True, exist_ok=True)

    def file_exists(self, relative_path):
        """Check if a file exists relative to output directory."""
        file_path = self.output / relative_path
        return file_path.exists()
