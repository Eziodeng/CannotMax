import os
import subprocess
import time

import cv2

adb_path = r".\platform-tools\adb.exe"
print(f"ADB路径: {adb_path}")

device_serial = '127.0.0.1:5555'  # 指定设备序列号

process_images = [cv2.imread(f'images/process/{i}.png') for i in range(13)]

# 屏幕分辨率
screen_width = 1920
screen_height = 1080

relative_points = [
    (0.9297, 0.8833),  # 右ALL、返回主页、加入赛事、开始游戏
    (0.0713, 0.8833),  # 左ALL
    (0.8281, 0.8833),  # 右礼物、自娱自乐
    (0.1640, 0.8833),  # 左礼物
    (0.4979, 0.6324),  # 本轮观望
]


def connect_to_emulator():
    # 预设的device_serial列表
    global device_serial
    device_serials = [device_serial,
                      "127.0.0.1:5554",
                      "127.0.0.1:16384",

                      "127.0.0.1:5552",
                      "127.0.0.1:5553",
                      "127.0.0.1:5555",
                      "127.0.0.1:5556",

                      "127.0.0.1:16382",
                      "127.0.0.1:16383",
                      "127.0.0.1:16385",
                      "127.0.0.1:16386",
                      ]

    for device_serial_ in device_serials:
        try:
            # 使用绝对路径连接到模拟器
            subprocess.run(f'{adb_path} connect {device_serial_}', shell=True, check=True)
            print(f"Successfully connected to {device_serial_}")
            return  # 连接成功则退出函数
        except subprocess.CalledProcessError as e:
            print(f"Failed to connect to {device_serial_}, trying next...")
            last_error = e  # 保存最后一个错误
        except FileNotFoundError as e:
            print(f"Error: {e}. Please ensure adb is installed and added to the system PATH.")
            return  # 如果是adb路径问题，直接返回

    # 如果所有尝试都失败
    print(f"ADB Port Error: {last_error} \n"
          f"Please refer to (LeiDian) https://help.ldmnq.com/docs/LD9adbserver  \n"
          f"(MUMU) https://mumu.163.com/help/20230214/35047_1073151.html")


connect_to_emulator()


def capture_screenshot():
    try:
        subprocess.run(f'{adb_path} -s {device_serial} shell screencap -p /sdcard/screenshot.png', shell=True,
                       check=True)
        subprocess.run(f'{adb_path} -s {device_serial} pull /sdcard/screenshot.png screenshot.png', shell=True,
                       check=True)
        return cv2.imread('screenshot.png')
    except subprocess.CalledProcessError as e:
        print(f"Screenshot capture failed: {e}")
        return None


def match_images(screenshot, templates):
    screenshot_quarter = screenshot[int(screenshot.shape[0] * 3 / 4):, :]
    results = []
    for idx, template in enumerate(templates):
        template_quarter = template[int(template.shape[0] * 3 / 4):, :]
        res = cv2.matchTemplate(screenshot_quarter, template_quarter, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        results.append((idx, max_val))
    return results


def click(point):
    x, y = point
    x_coord = int(x * screen_width)
    y_coord = int(y * screen_height)
    print(f"点击坐标: ({x_coord}, {y_coord})")
    subprocess.run(f'{adb_path} -s {device_serial} shell input tap {x_coord} {y_coord}', shell=True)


def operation_simple(results):
    for idx, score in results:
        if score > 0.6:  # 假设匹配阈值为 0.8
            if idx == 0:  # 加入赛事
                click(relative_points[0])
                print("加入赛事")
            elif idx == 1:  # 自娱自乐
                click(relative_points[2])
                print("自娱自乐")
            elif idx == 2:  # 开始游戏
                click(relative_points[0])
                print("开始游戏")
            elif idx in [3, 4, 5]:  # 本轮观望
                click(relative_points[4])
                print("本轮观望")
            elif idx in [10, 11]:
                print("下一轮")
            elif idx in [6, 7]:
                print("等待战斗结束")
            elif idx == 12:  # 返回主页
                click(relative_points[0])
                print("返回主页")
            break  # 匹配到第一个结果后退出

def operation(results):
    for idx, score in results:
        if score > 0.6:  # 假设匹配阈值为 0.8
            if idx in [3, 4, 5]:
                # 识别怪物类型数量，导入模型进行预测
                prediction = 0.6
                # 根据预测结果点击投资左/右
                if prediction > 0.5:
                    click(relative_points[1])  # 投资右
                    print("投资右")
                else:
                    click(relative_points[0])  # 投资左
                    print("投资左")
            elif idx in [1, 5]:
                click(relative_points[2])  # 点击省点饭钱
                print("点击省点饭钱")
            elif idx == 2:
                click(relative_points[3])  # 点击敬请见证
                print("点击敬请见证")
            elif idx in [3, 4]:
                # 保存数据
                click(relative_points[4])  # 点击下一轮
                print("点击下一轮")
            elif idx == 6:
                print("等待战斗结束")
            break  # 匹配到第一个结果后退出

def main():
    while True:
        screenshot = capture_screenshot()
        if screenshot is not None:
            results = match_images(screenshot, process_images)
            results = sorted(results, key=lambda x: x[1], reverse=True)
            print("匹配结果：", results[0])
            operation(results)
        time.sleep(2)


if __name__ == "__main__":
    main()
