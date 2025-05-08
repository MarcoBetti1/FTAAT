import hashlib
from pathlib import Path

def generate_prompt_id_from_template(template_path="prompt_template.j2"):
    """
    Returns a deterministic short ID based on the prompt template file.
    """
    path = Path(template_path)
    if not path.exists():
        return "default_prompt"
    tpl = path.read_text()
    h = hashlib.sha1(tpl.encode()).hexdigest()
    return "tpl_" + h[:8]
