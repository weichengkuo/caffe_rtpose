import os
import numpy as np
import pdb
import videoHandler
import tempfile
import time
from functools import wraps
import subprocess
from joblib import Parallel, delayed

def time_this(func):
  @wraps(func)
  def decorated_func(*args):
    start_time = time.time()
    output = func(*args)
    time_taken = time.time() - start_time
    return output,time_taken 

  return decorated_func

time_uzVideo = time_this(videoHandler.uzVideo)
time_closeVideo = time_this(videoHandler.closeVideo)
time_cmd = time_this(os.system)
time_subproc = time_this(subprocess.Popen)

VIDEO_DIR = './fouhey_clips'
rtp_command = './build/examples/rtpose/rtpose.bin --image_dir {} --write_json ./output/json/{} --write_frames {} --no_display --no_frame_drops'
video_files = os.listdir(VIDEO_DIR)
num_video_files = len(video_files)
NUM_THREAD = 6

def process_single_video(fnum_id,fname):
  """
  Function to process single video
  """
  video_name = fname.split('.')[0]
  print('Decompressing videos to image sequence')
  frameFolder,uzTime = time_uzVideo(os.path.join(VIDEO_DIR,fname))
  outframeFolder = tempfile.mkdtemp()
  full_cmd = rtp_command.format(frameFolder,video_name,outframeFolder)
  if not os.path.exists('./output/json/'+video_name):
    os.mkdir('./output/json/'+video_name)

  #Run the rtp
  print('Running RTP {}/{}:\n {}'.format(fnum_id,num_video_files,full_cmd))
  os_out, rtp_time = time_cmd(full_cmd) 
  if os_out:
    raise RuntimeError("Failure command {}".format(full_cmd))

  # start_time = time.time()
  # process = subprocess.Popen([full_cmd],shell=True)
  # process.wait()
  # rtp_time = time.time()-start_time
  frame_num = len(os.listdir(outframeFolder))
  if frame_num == 0:
    return None,None,None,None,None 

  #Read output frames to write videos
  out_vid = 'output/videos/{}'.format(fname)
  if os.path.exists(out_vid):
    os.system('rm '+out_vid)

  if not os.path.exists(outframeFolder):
    raise RuntimeError("Folder doesn't exist: {}".format(outframeFolder))

  conv_cmd = '{} -i {}/frame%06d.jpg {}'.format(videoHandler.FFMPEG_STATIC,outframeFolder,out_vid)
  print('Writing frames to video: \n {}'.format(conv_cmd))
  conv_out, write_time = time_cmd(conv_cmd)
  if conv_out:
    raise RuntimeError("Failure command {}".format(conv_cmd))

  __, close_time = time_closeVideo(frameFolder)
  __, close_time2 = time_closeVideo(outframeFolder)
  close_time += close_time2
  total_time = uzTime + rtp_time + write_time + close_time
  time_per_frame = total_time/frame_num

  log_str = '{} write_seq {:.1f}s, rtp {:.1f}s, total_time {:.1f}s, NumFrame {:d}, tpf {:.2f}s \n'.format(video_name,write_time,rtp_time,total_time,frame_num,time_per_frame)
  # runtime_log_fid.write(log_str)

  return write_time, rtp_time, total_time, frame_num, log_str

def main():
  runtime_log_fid = open('log/process_video_log_2.txt','w')
  acc_time = {'uzTime':None,'rtp':None,'total':None,'frame_num':None,'tpf':None}
  #Parallel
  all_time_info = Parallel(n_jobs=NUM_THREAD)(delayed(process_single_video)(fnum_id,fname) for fnum_id,fname in enumerate(video_files))

  acc_time['write_time'] = sum([info[0] for info in all_time_info])
  acc_time['rtp'] = sum([info[1] for info in all_time_info])
  acc_time['total'] = sum([info[2] for info in all_time_info])
  acc_time['frame_num'] = sum([info[3] for info in all_time_info])
  acc_time['tpf'] = acc_time['total']/acc_time['frame_num']
  log_strs = [info[4] for info in all_time_info]

  for log_str in log_strs:
    runtime_log_fid.write(log_str)

  log_str = 'Summary: write_time {:.1f}s, rtp {:.1f}s, total_time {:.1f}s, NumFrame {:d}, tpf {:.2f}s \n'.format(acc_time['write_time'],acc_time['rtp'],acc_time['total'],acc_time['frame_num'],acc_time['total']/acc_time['frame_num'])
  runtime_log_fid.write(log_str)
  runtime_log_fid.close()

if __name__ == '__main__':
  main()
