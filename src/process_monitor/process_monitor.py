import json
import os.path
import sys
import time
from glob import glob

CHILDREN = set()


def get_children(pr):
    try:
        children = pr.children(recursive=True)
        CHILDREN.update(set(children))
    except:
        pass

    return CHILDREN


def monitor(pid, interval=None, include_children=False):
    """
    Based on: https://github.com/astrofrog/psrecord
    Copyright (c) 2013, Thomas P. Robitaille
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
    """

    # We import psutil here so that the module can be imported even if psutil
    # is not present (for example if accessing the version)
    import psutil

    print(pid)

    pr = psutil.Process(pid)
    name = pr.name()

    # Record start time
    start_time = time.time()

    log = {}
    log["times"] = []
    log["cpu"] = []
    log["mem_real"] = []
    log["mem_virtual"] = []
    log["file_imported_at"] = 0
    log["file_loaded_at"] = 0

    state = 0

    # Start main event loop
    while True:

        try:

            # Find current time
            current_time = time.time()

            try:
                pr_status = pr.status()
            except TypeError:  # psutil < 2.0
                pr_status = pr.status
            except psutil.NoSuchProcess:  # pragma: no cover
                break

            # Check if process status indicates we should exit
            if pr_status in [psutil.STATUS_ZOMBIE, psutil.STATUS_DEAD]:
                print("Process finished ({0:.2f} seconds)".format(current_time - start_time))
                break

            # Get current CPU and memory
            try:
                with pr.oneshot():
                    current_cpu = pr.cpu_percent()
                    current_mem = pr.memory_info()
            except Exception:
                break
            current_mem_real = current_mem.rss / 1024.0 ** 2
            current_mem_virtual = current_mem.vms / 1024.0 ** 2

            # Get information for children
            if include_children:
                for child in get_children(pr):
                    try:
                        with child.oneshot():
                            current_cpu += child.cpu_percent()
                            current_mem = child.memory_info()
                    except Exception:
                        continue
                    current_mem_real += current_mem.rss / 1024.0 ** 2
                    current_mem_virtual += current_mem.vms / 1024.0 ** 2

            if interval is not None:
                time.sleep(interval)

            log["times"].append(current_time - start_time)
            log["cpu"].append(current_cpu)
            log["mem_real"].append(current_mem_real)
            log["mem_virtual"].append(current_mem_virtual)

        except KeyboardInterrupt:  # pragma: no cover
            if state == 0:
                log["file_imported_at"] = time.time() - start_time
                state += 1
                print(f'{log["file_imported_at"]=}')
            elif state == 1:
                log["file_loaded_at"] = time.time() - start_time
                state += 1
                print(f'{log["file_loaded_at"]=}')
            else:
                break

    return name, log


def plot(log, file_name):
    """
    Based on: https://github.com/astrofrog/psrecord
    Copyright (c) 2013, Thomas P. Robitaille
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
    SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
    INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
    CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    POSSIBILITY OF SUCH DAMAGE.
    """

    import matplotlib.pyplot as plt

    with plt.rc_context({"backend": "Agg"}):

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.plot(log["times"], log["cpu"], "-", lw=1, color="r")

        ax.set_ylabel("CPU (%)", color="r")
        ax.set_xlabel("time (s)")
        ax.set_ylim(0.0, max(log["cpu"]) * 1.2)

        ax2 = ax.twinx()

        ax2.plot(log["times"], log["mem_real"], "-", lw=1, color="b")
        ax2.set_ylim(0.0, max(log["mem_real"]) * 1.2)

        ax2.set_ylabel("Real Memory (MB)", color="b")

        ax.grid()

        ax.vlines(
            [val for val in [log["file_imported_at"], log["file_loaded_at"]] if val > 0],
            0.0,
            max(log["cpu"]) * 1.2,
            linestyle="dashed",
        )

        print(f'{file_name}: Max CPU: {max(log["cpu"])}, Max MEM: {max(log["mem_real"])}')

        fig.savefig(file_name)


if __name__ == "__main__":
    # start_time = time.time()
    # data = []

    # p = psutil.Process(int(sys.argv[1]))
    # name = p.name()

    # while p.is_running():
    #     try:
    #         entry = p.as_dict()
    #     except:
    #         break
    #     entry["time_since_capture_started"] = time.time() - start_time
    #     data.append(entry)
    #     time.sleep(1)

    if len(sys.argv) > 1:
        name, log = monitor(int(sys.argv[1]), interval=None, include_children=True)

        with open(f"process_log_{name}.json", "w") as out_file:
            json.dump(log, out_file, indent=4)

        plot(log, f"process_log_{name}.png")

    for path in glob("*.json"):
        log = json.load(open(path))
        plot(log, path.replace("json", "png"))
