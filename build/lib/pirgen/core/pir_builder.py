# core/pir_builder.py
from io import StringIO
from .project_model import ProjectModel


class PIRBuilder:
    def __init__(self, model: ProjectModel, with_profiles: bool = False):
        self.model = model
        self.with_profiles = with_profiles

    def build(self) -> str:
        if not self.model.deps_finalized:
            raise RuntimeError(
                "Dependencies not finalized. Call model.finalize_dependencies() first."
            )

        output = StringIO()
        output.write("<pir>\n")

        meta = self._build_meta()
        if meta:
            output.write(meta)
            output.write("\n")

        units = self._build_units()
        if units:
            output.write(units)
            output.write("\n")

        dep_pool = self._build_dependency_pool()
        if dep_pool:
            output.write(dep_pool)
            output.write("\n")

        deps = self._build_dependencies()
        if deps:
            output.write(deps)
            output.write("\n")

        symbols = self._build_symbols()
        if symbols:
            output.write(symbols)
            output.write("\n")

        profiles = self._build_profiles()
        if profiles and self.with_profiles:
            output.write(profiles)
            output.write("\n")

        layout = self._build_layout()
        if layout:
            output.write(layout)
            output.write("\n")

        snippets = self._build_snippets()
        if snippets:
            output.write(snippets)
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
        return f"<meta>\nname: {self.model.name}\nroot: {root}\nlang: {langs}\n</meta>"

    def _build_units(self) -> str:
        lines = ["<units>"]
        for u in self.model.units:
            if u.role == "lib":
                lines.append(f"{u.uid}: {u.path} type={u.lang} module={u.module}")
            else:
                lines.append(
                    f"{u.uid}: {u.path} type={u.lang} role={u.role} module={u.module}"
                )
        lines.append("</units>")
        return "\n".join(lines)

    def _build_dependency_pool(self) -> str:
        if not self.model.dep_pool_items:
            return ""
        lines = ["<dependency-pool>"]
        for did, verb, target in self.model.dep_pool_items:
            lines.append(f"{did}: {verb}:{target}")
        lines.append("</dependency-pool>")
        return "\n".join(lines)

    def _build_dependencies(self) -> str:
        if not self.model.dep_refs:
            return ""
        lines = ["<dependencies>"]
        for uid in sorted(self.model.dep_refs, key=lambda x: int(x[1:])):
            refs = self.model.dep_refs[uid]
            if refs:
                lines.append(f"{uid}:{' '.join(refs)}")
        lines.append("</dependencies>")
        return "\n".join(lines)

    def _build_symbols(self) -> str:
        if not self.model.symbols:
            return ""
        lines = ["<symbols>"]
        for s in self.model.symbols:
            attrs = (
                " " + ", ".join(f"{k}={v}" for k, v in sorted(s.attrs.items()))
                if s.attrs
                else ""
            )
            lines.append(f"{s.name}:{s.unit_uid} {s.kind}{attrs}")
        lines.append("</symbols>")
        return "\n".join(lines)

    def _build_profiles(self) -> str:
        if not self.model.profiles:
            return ""
        lines = ["<profiles>"]
        if self.model.active_profile:
            lines.append(f"  active: {self.model.active_profile}")
        for profile_name, profile_data in sorted(self.model.profiles.items()):
            confidence = profile_data.get("confidence", 0.0)
            tags = profile_data.get("tags", [])
            signals = profile_data.get("signals", [])
            lines.append(f"  {profile_name}:")
            lines.append(f"    confidence: {confidence}")
            if tags:
                lines.append("    tags:")
                for tag in sorted(tags):
                    lines.append(f"      - {tag}")
            if signals:
                lines.append("    signals:")
                for signal in sorted(signals):
                    lines.append(f"      - {signal}")
        lines.append("</profiles>")
        return "\n".join(lines)

    def _build_layout(self) -> str:
        if not self.model.layout_lines:
            return ""
        return "\n".join(["<layout>", *self.model.layout_lines, "</layout>"])

    def _build_snippets(self) -> str:
        if not self.model.snippets:
            return ""
        lines = ["<code-snippets>"]
        for uid, content in self.model.snippets:
            lines.extend(
                [
                    f'<snippet unit="{uid}">',
                    "<![CDATA[",
                    content.strip(),
                    "]]>",
                    "</snippet>",
                ]
            )
        lines.append("</code-snippets>")
        return "\n".join(lines)
