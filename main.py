'''
mp3转wav

wav分块

wav提取
'''
import os
import re
import shutil

from paddlespeech.cli.asr import ASRExecutor
from paddlespeech.cli.text import TextExecutor
from pydub import AudioSegment

from app.logging import get_logger

logging = get_logger(__name__)

CHUNK_DATA_PATH = "./data/chunks"
CHUNK_LENGTH_MS = 49 * 1000


def mp3_to_wav(mp3_file):
    """
    将 MP3 文件转换为 WAV 格式
    :param mp3_file: 输入的 MP3 文件路径
    :param wav_file: 输出的 WAV 文件路径
    """
    # 加载 MP3 文件
    audio = AudioSegment.from_mp3(mp3_file)
    absolute_path = os.path.abspath(mp3_file)
    wav_file = re.sub(r'\.mp3$', '.wav', absolute_path)
    # 导出为 WAV 文件
    audio.export(wav_file, format="wav", bitrate="16k")
    logging.info(f"转换完成：{wav_file}")
    return wav_file


def split_audio_into_chunks(audio_file_path, chunk_length_ms, output_folder):
    # 加载音频文件
    audio = AudioSegment.from_file(audio_file_path)
    audio = audio.set_frame_rate(16000)
    # 创建输出文件夹（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 计算总时长和分割数量
    total_length = len(audio)
    num_chunks = total_length // chunk_length_ms

    # 分割音频
    for i in range(num_chunks):
        start_time = i * chunk_length_ms
        end_time = (i + 1) * chunk_length_ms
        chunk = audio[start_time:end_time]
        chunk.export(os.path.join(output_folder, f"chunk_{i}.wav"), format="wav")

    # 处理剩余部分
    if total_length % chunk_length_ms != 0:
        start_time = num_chunks * chunk_length_ms
        chunk = audio[start_time:]
        chunk.export(os.path.join(output_folder, f"chunk_{num_chunks}.wav"), format="wav")
    logging.info(f"切片完成：{os.path.abspath(output_folder)}")
    return num_chunks

def delete_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
    logging.info(f"切片删除完成：{os.path.abspath(folder_path)}")




if __name__ == '__main__':
    delete_files_in_folder('./exp/log')
    wav_file = mp3_to_wav("./data/voice.mp3")
    if not os.path.exists('./data/chunks'):
        os.makedirs('./data/chunks')
    num_chunks = split_audio_into_chunks(wav_file, CHUNK_LENGTH_MS, CHUNK_DATA_PATH)
    asr = ASRExecutor()
    text_punc = TextExecutor()
    text = ''
    for i in range(0, num_chunks):
        result = asr(audio_file=f"./data/chunks/chunk_{i}.wav")
        result = text_punc(text=result)
        print(result)
        text += result
    delete_files_in_folder(CHUNK_DATA_PATH)
    txt_path = re.sub(r'\.wav$', '.txt', wav_file)
    with open(txt_path, 'w') as f:
        f.write(text)