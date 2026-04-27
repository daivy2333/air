from io import StringIO
from .project_model import ProjectModel


class PIRBuilder:
    def __init__(self, model: ProjectModel):
        self.model = model

    def build(self) -> str:
        if not self.model.deps_finalized:
            raise RuntimeError(
                "Dependencies not finalized. Call model.finalize_dependencies() first."
            )

        output = StringIO()
        output.write("<pir>\n")
        output.write(self._build_meta())
        output.write("\n")
        output.write(self._build_units())
        output.write("\n")
        output.write(self._build_pool())
        output.write("\n")
        output.write(self._build_deps())
        output.write("\n")
        output.write(self._build_syms())
        output.write("\n")
        output.write("</pir>")
        return output.getvalue()

    def _build_meta(self) -> str:
        import os

        langs = ",".join(sorted(self.model.langs))
        root = self.model.root
        if os.path.isabs(root):
            try:
                rel = os.path.relpath(root)
                if not rel.startswith(".."):
                    root = rel
            except ValueError:
                pass
        return f"<meta>\n{self.model.name}|{root}|{langs}\n</meta>"

    def _build_units(self) -> str:
        lines = ["<units>"]
        for u in self.model.units:
            if u.role == "lib":
                lines.append(f"{u.uid}|{u.path}|{u.lang}|{u.module}")
            else:
                lines.append(f"{u.uid}|{u.path}|{u.lang}|{u.role}|{u.module}")
        lines.append("</units>")
        return "\n".join(lines)

    def _build_pool(self) -> str:
        if not self.model.dep_pool_items:
            return ""
        lines = ["<pool>"]
        for did, verb, target in self.model.dep_pool_items:
            lines.append(f"{did}|{verb}|{target}")
        lines.append("</pool>")
        return "\n".join(lines)

    def _build_deps(self) -> str:
        if not self.model.dep_refs:
            return ""
        lines = ["<deps>"]
        for uid in sorted(self.model.dep_refs, key=lambda x: int(x[1:])):
            refs = self.model.dep_refs[uid]
            if refs:
                lines.append(f"{uid}|{' '.join(refs)}")
        lines.append("</deps>")
        return "\n".join(lines)

    def _build_syms(self) -> str:
        if not self.model.symbols:
            return ""
        lines = ["<syms>"]
        for s in self.model.symbols:
            if s.attrs:
                attrs = "|" + "|".join(
                    f"{k}" for k, v in sorted(s.attrs.items()) if v == "true"
                )
                lines.append(f"{s.name}|{s.unit_uid}|{s.kind}{attrs}")
            else:
                lines.append(f"{s.name}|{s.unit_uid}|{s.kind}")
        lines.append("</syms>")
        return "\n".join(lines)
