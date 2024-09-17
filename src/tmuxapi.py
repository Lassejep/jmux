import subprocess
from typing import List


class TmuxBin():
    def __init__(self) -> None:
        self.tmux_bin = self._find_tmux_bin()

    class TmuxError(Exception):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    class TmuxNotFoundError(TmuxError):
        def __init__(self, message: str) -> None:
            self.message = message
            super().__init__(self.message)

    def run(self, cmd: List[str]) -> str:
        try:
            cmd.insert(0, self.tmux_bin)
            return subprocess.check_output(cmd, text=True).strip()
        except subprocess.CalledProcessError as err:
            raise self.TmuxError(f"Failed to run {err}")

    def _find_tmux_bin(self) -> str:
        try:
            return subprocess.check_output(["which", "tmux"],
                                           text=True).strip()
        except subprocess.CalledProcessError as err:
            raise self.TmuxNotFoundError("Tmux not found") from err

    def get(self, keys: str | List[str], target: str = "") -> str:
        cmd = ["display-message"]
        if target:
            cmd.extend(["-t", target])
        if type(keys) is not list:
            keys = [keys]
        keystr = ""
        for key in keys:
            keystr += f"#{{{key}}}:"
        cmd.extend(["-p", f"{keystr[:-1]}"])
        output = self.run(cmd).split(":")
        if len(output) == 1:
            return output[0]
        return output

    def send_keys(self, keys: str | List[str], target: str) -> None:
        if type(keys) is not list:
            keys = [keys]
        wait_cmd = f"; {self.tmux_bin} wait-for -S jmux_ready"
        cmd = ["send-keys", "-t", target, *keys, wait_cmd, "C-m", "C-l"]
        confirm_cmd = [self.tmux_bin, "wait-for", "jmux_ready"]
        try:
            confirm_proc = subprocess.Popen(confirm_cmd)
            self.run(cmd)
        except self.TmuxError:
            confirm_proc.kill()
            raise self.TmuxError("Failed to send keys" + keys)
        try:
            confirm_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            confirm_proc.kill()


TMUX = TmuxBin()
