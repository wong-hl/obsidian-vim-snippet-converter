import json
from typing import Optional
import re

PATH_TO_JSON = "obsidian_snippets.json"

def load_json_file():
    with open(PATH_TO_JSON) as json_file:
        return json.load(json_file)
    
obsidian_snippet_variables: dict[str, str] = {
	"${GREEK}": "alpha|beta|gamma|Gamma|delta|Delta|epsilon|varepsilon|zeta|eta|theta|vartheta|Theta|iota|kappa|lambda|Lambda|mu|nu|xi|omicron|pi|rho|varrho|sigma|Sigma|tau|upsilon|Upsilon|phi|varphi|Phi|chi|psi|omega|Omega",
	"${SYMBOL}": "parallel|perp|partial|nabla|hbar|ell|infty|oplus|ominus|otimes|oslash|square|star|dagger|vee|wedge|subseteq|subset|supseteq|supset|emptyset|exists|nexists|forall|implies|impliedby|iff|setminus|neg|lor|land|bigcup|bigcap|cdot|times|simeq|approx",
	"${MORE_SYMBOLS}": "leq|geq|neq|gg|ll|equiv|sim|propto|rightarrow|leftarrow|Rightarrow|Leftarrow|leftrightarrow|to|mapsto|cap|cup|in|sum|prod|exp|ln|log|det|dots|vdots|ddots|pm|mp|int|iint|iiint|oint"
}

class ObsidianSnippet:
    trigger: str
    replacement: str
    options: str
    priority: Optional[int]
    description: Optional[str]
    flags: Optional[str]

    def __init__(self, trigger: str, replacement: str, options: str, 
    priority: Optional[int] = None, description: Optional[str] = None, 
    flags: Optional[str] = None):
        self.trigger = trigger
        self.replacement = replacement
        self.options = options
        self.priority = priority
        self.description = description
        self.flags = flags

    def math_context(self):
        math_chars: list[str] = ["m", "M", "n"]
        return "context \"math()\"\n" if any(math_char in self.options for math_char in math_chars) else ""

    def output_priority(self):
        return f"priority {int(self.priority)}\n" if self.priority is not None else ""

    def convert_options(self):
        converted: str = ""
        for c in self.options:
            match c:
                case 'c':
                    raise ValueError(f"option is {c}")
                case 'A' | 'r' | 'w':
                    converted += f"{c}"
                case 'm' | 'M' |'n':
                    converted += "i"
                # do nothing for 't' case
        return converted

    def is_regex(self):
        return 'r' in self.options

    def generate_replacement(self):
        replacement: str = self.replacement
        if self.is_regex():
            replacement = replacement.replace("[[0]]", "`!p snip.rv = match.group(1)`")
            replacement = replacement.replace("[[1]]", " `!p snip.rv = match.group(2)`")
        return replacement 

    def generate_trigger(self):
        trigger: str = self.trigger
        if self.is_regex():
            trigger = trigger.replace("\n", "\\n") 
            for snippet_var, replacement in obsidian_snippet_variables.items():
                trigger = trigger.replace(snippet_var, replacement)
            trigger = f"\"{re.escape(trigger)}\""
        return trigger

    def generate_description(self):
        if self.description is None:
            return "\"\""
        else:
            return f"\"{self.description}\""

    def generate_snippet(self):
        output: str = f"{self.output_priority()}"
        output += f"{self.math_context()}"
        output += f"snippet {self.generate_trigger()} {self.generate_description()} {self.convert_options()}\n"
        output += self.generate_replacement() + "\nendsnippet"
        return output




if __name__ == "__main__":
    math_context: str = """
# Include this code block at the top of a *.snippets file...
# ----------------------------- #
global !p
def math():
    return vim.eval('vimtex#syntax#in_mathzone()') == '1'
endglobal
    """
    snippets = "\n\n".join([ObsidianSnippet(**item).generate_snippet() for item in load_json_file()])

    with open("math.snippets", 'w') as output_file:
        print(math_context + "\n" + snippets, file=output_file)


