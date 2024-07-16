from os import mkdir

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.ticker import MultipleLocator, FuncFormatter

from datetime import datetime

from utils.analyzers import get_bitrate, get_min_avg_max
from utils.converters import epoch_to_datetime
from utils.fs_ops import create_directory








def create_files(
    ip_list: list, path_to_csv: str, epoch_start: int, epoch_end: int
) -> None:

    date_duration = f'{epoch_to_datetime(epoch_start).replace(" ","_")}_{epoch_to_datetime(epoch_end).replace(" ","_")}'

    create_directory(f"./plots/recording_{date_duration}")

    if len(ip_list) > 1:
        create_directory(f"./plots/recording_{date_duration}/multiple")

    for ip in ip_list:
        create_directory(f"./plots/recording_{date_duration}/{ip}")

    min_avg_max_values = get_min_avg_max(
        ip_list, path_to_csv, epoch_start, epoch_end
    )

    for ip in ip_list:

        if min_avg_max_values[ip]:

            minimum, average, maximum = min_avg_max_values[ip]

            with open(
                f"./plots/recording_{date_duration}/{ip}/bitrate_info.txt",
                "a",
                encoding="utf-8",
            ) as file:
                lines = [
                    f"Минимальный битрейт: {str(minimum / 1000)} kbps\n",
                    f"Средний битрейт: {str(average / 1000)} kbps\n",
                    f"Максимальный битрейт: {str(maximum / 1000)} kbps\n",
                ]

                file.writelines(lines)

    ylim = create_plot(ip_list, path_to_csv, epoch_start, epoch_end)

    if len(ip_list) > 1:
        for ip in ip_list:
            create_plot(
                [ip],
                path_to_csv,
                epoch_start,
                epoch_end,
                ylim,
                ip_list.index(ip),
            )


if __name__ == "__main__":
    pass
