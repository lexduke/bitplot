from datetime import datetime

from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter, MultipleLocator
from utils.analyzers import get_bitrate
from utils.converters import epoch_to_datetime
from matplotlib.style import use as use_style


def create(
    ip_list: list,
    path_to_csv: str,
    epoch_start: int,
    epoch_end: int,
    ylim: int | None = None,
    enum: int = 1,
) -> int | None:

    date_start: str = epoch_to_datetime(epoch_start).replace(" ", "_")
    date_end: str = epoch_to_datetime(epoch_end).replace(" ", "_")
    date_duration: str = f"{date_start}_{date_end}"
    epoch_delta: int = epoch_end - epoch_start

    date_list = [
        datetime.fromtimestamp(i)
        for i in range(epoch_start, epoch_end + 1, 1)
    ]

    use_style("seaborn-v0_8")

    fig, ax = plt.subplots(layout="constrained")

    for ip in ip_list:
        if len(ip_list) > 1:
            ax.plot(
                date_list,
                get_bitrate(path_to_csv, ip, range(epoch_start, epoch_end + 1, 1)),
                label=ip,
                alpha=0.8,
            )
        else:
            ax.plot(
                date_list,
                get_bitrate(path_to_csv, ip, range(epoch_start, epoch_end + 1, 1)),
                label=ip,
                color="C" + str(enum),
            )
    ax.set_ylabel("Битрейт")
    if ylim:
        ax.set_ylim(*ylim)
    else:
        ax.set_ylim(0)
    ylim = ax.get_ylim()
    ax.yaxis.set_major_locator(MultipleLocator(5 * 10**5))

    def millions_formatter(y, pos):
        return "%1dkbps" % (y * 1e-3)

    ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    ax.set_xlabel("Дата")
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S\n%d-%m-%Y"))

    ax.set_title("График битрейта")
    ax.legend()
    fig.set_size_inches(19.2, 10.8)

    if len(ip_list) > 1:
        image_name = (
            f"./plots/recording_{date_duration}/multiple/multiple_{date_duration}.png"
        )
    else:
        str_ip = str(*ip_list)
        image_name = (
            f"./plots/recording_{date_duration}/{str_ip}/{str_ip}_{date_duration}.png"
        )

    plt.savefig(image_name, bbox_inches="tight", dpi=200)

    if (
        epoch_delta <= 2000
    ):  # Прекратить выполнение при длительности записи менее 2000 сек
        plt.close(fig)
        return ylim

    epoch_start_limit = (epoch_start // 1800) * 1800
    epoch_end_limit = (epoch_end // 1800 + 1) * 1800

    limits_list = [
        [i, i + 1800] for i in range(epoch_start_limit, epoch_end_limit, 1800)
    ]

    for segment in limits_list:
        segment_duration = f'{epoch_to_datetime(segment[0]).replace(" ","_")}_{epoch_to_datetime(segment[1]).replace(" ","_")}'
        if len(ip_list) > 1:
            image_name = f"./plots/recording_{date_duration}/multiple/multiple_{segment_duration}.png"
        else:
            str_ip = str(*ip_list)
            image_name = f"./plots/recording_{date_duration}/{str_ip}/{str_ip}_{segment_duration}.png"

        ax.set_xlim(
            left=datetime.fromtimestamp(segment[0]),
            right=datetime.fromtimestamp(segment[1]),
        )
        plt.savefig(image_name, bbox_inches="tight", dpi=200)
        plt.close(fig)

    return ylim






def create_plot():

    x = [
        datetime.fromtimestamp(i)
        for i in range(epoch_start, epoch_end + 1, 1)
    ]
    y = get_bitrate(
        path_to_csv,
        ip,
        range(epoch_start, epoch_end + 1, 1)
    )

    fig, ax = plt.subplots()


def create_multiplot():
    pass