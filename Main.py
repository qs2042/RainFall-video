from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List

import json
import re
import requests


@dataclass
class Video:
    id: str
    name: str
    pic: str
    desc: str


@dataclass
class BiliBiliVideo(Video):
    def __init__(self):
        pass

    aid: str
    bvid: str


class VideoInterface(ABC):
    def __init__(self):
        self.session = requests.session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.5; Win64; x64) AppleWebKit/547.36 (KHTML, like Gecko) Chrome/86.0.4280.66 Safari/537.36"
        }

    @abstractmethod
    def searchVideo(self, video_name) -> List[Video]:
        """
        搜索视频
        :param video_name: 视频关键词
        :return: 视频列表
        """
        pass

    @abstractmethod
    def searchVideoByUserId(self, user_id) -> List[Video]:
        """
        获取用户发表的所有视频
        :param user_id: 用户ID
        :return: 视频列表
        """
        pass

    @abstractmethod
    def download(self, video: Video):
        """
        下载视频
        :param video:
        :return:
        """
        pass


class BiliBiliVideoImpl(VideoInterface):

    def searchVideo(self, video_name) -> List[BiliBiliVideo]:
        pass

    def searchVideoByUserId(self, user_id) -> List[BiliBiliVideo]:
        pn = 1
        ps = 30
        ps_max = None
        pn_max = None

        l = []
        while True:
            url = f"https://api.bilibili.com/x/space/arc/search?mid={user_id}&ps={ps}&tid=0&pn={pn}&keyword=&order=pubdate&jsonp=jsonp"
            self.session.headers["origin"] = "https://www.bilibili.com"
            res = self.session.get(url)
            res_json = json.loads(res.text)
            if res_json["code"] != 200:
                print(res_json)
                break

            data = res_json["data"]

            # 列表: tlist, vlist
            list = data["list"]

            # 页数: pn, ps, count
            page = data["page"]

            if pn_max is None:
                ps_max = page["count"]
                pn_max = (int(page["count"]) + ps - 1) // ps
            elif pn > pn_max:
                break

            for i in list["vlist"]:
                b = BiliBiliVideo()
                b.name = i["title"]
                b.pic = i["pic"]
                b.desc = i["description"]
                b.aid = i["aid"]
                b.bvid = i["bvid"]
                l.append(b)

            pn += 1

        print(f"运行结束, 总共{ps_max}个数据, 按照{ps}一页, 共{pn_max}页, 当前已获取到第{pn}页的数据")
        return l

    def download(self, video: BiliBiliVideo):
        data = self.getVideoInfo(video)
        downloadVideo, downloadAudio = self.getDonwload(data.get("resJson"))
        with open("%s.mp4" % video.bvid, "wb") as f:
            f.write(self.session.get(downloadVideo).content)
        with open("%s.mp3" % video.bvid, "wb") as f:
            f.write(self.session.get(downloadAudio).content)

        print("运行结束, 默认为视频/音频分离, 可通过设置将输出更改为一个文件")

    def getDonwload(self, resJson):
        data = resJson["data"]
        # quality = data["quality"]
        # timelength = data["timelength"]
        # accept_format = data["accept_format"]
        # accept_description = data["accept_description"]
        # accept_quality = data["accept_quality"]
        # video_codecid = data["video_codecid"]

        dash = data["dash"]
        video = dash["video"]
        audio = dash["audio"]

        if (len(video)) == 0:
            return False

        downloadVideo = video[0]["baseUrl"]
        downloadAudio = audio[0]["baseUrl"]
        # baseUrl base_url
        # backupUrl backup_url      # Default: None 这个是列表
        # mimeType
        return downloadVideo, downloadAudio

    def getVideoInfo(self, video: BiliBiliVideo):
        url = f"https://www.bilibili.com/video/{video.bvid}"
        self.session.headers["referer"] = url
        res = self.session.get(url)
        res_text = res.text

        resRe = re.findall(r'\<script\>window\.__playinfo__=(.*?)\</script\>', res_text)
        resJson = json.loads(resRe[0])
        return {"res": res, "resRe": resRe, "resJson": resJson}


if __name__ == "__main__":
    video = BiliBiliVideoImpl()
    video_list = video.searchVideoByUserId("14215405") # 36157335
    print(video_list)

    b = BiliBiliVideo()
    b.bvid = "BV1P7411H7tX"
    video.download(b)
