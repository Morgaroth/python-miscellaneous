#!/usr/bin/env python3
import argparse
import os
import subprocess

__author__ = 'mateusz'

convert_checked = False


def execute_async(command, verbose=False):
    def prepare_command():
        cmd = command
        if isinstance(cmd, str):
            cmd = cmd.split(" ")
        if not isinstance(cmd, list):
            raise Exception("Neither string nor list passed to execute command")
        return cmd

    cmd = prepare_command()
    if verbose:
        print("executing command:\n\t%s" % cmd)
    process = subprocess.Popen(cmd, env=os.environ.copy(), stdout=subprocess.PIPE)
    return process


def execute(command, verbose=False):
    process = execute_async(command, verbose)
    out, err = process.communicate()
    ret_code = process.returncode
    return out, err, ret_code


class ConvertChecked(object):
    checked = False


class convert_command(object):
    @staticmethod
    def check_installation():
        if ConvertChecked.checked is False:
            (out, err, ret) = execute(['convert', '-version'])
            if ret != 0:
                raise Exception("convert method not installed in system.... install it before continue.")
            print("convert command installed.")
            ConvertChecked.checked = True


class CONVERT(convert_command):
    @staticmethod
    def convert_percent_async(percent, file_name, verbose=False):
        CONVERT.check_installation()
        output = "%d%%-%s" % (percent, file_name)
        print("Converting %s using %d%% ratio to %s..." % (file_name, percent, output))
        return output, execute_async(['convert', file_name, '-quality', '100', '-resize', '%d%%' % percent, output],
                                     verbose)

    @staticmethod
    def convert_percent(percent, file_name, verbose=False):
        (output, process) = CONVERT.convert_percent_async(percent, file_name, verbose)
        out, err = process.communicate()
        print(out,err)
        ret_code = process.returncode
        return output, (out, err, ret_code)


class GIF(convert_command):
    @staticmethod
    def create_async(files_list, output, frames_per_second=3.0, verbose=False):
        GIF.check_installation()
        delay = int(100 * 1.0 / frames_per_second)
        print("Making %s..." % output)
        return execute_async(['convert', '-delay', str(delay), '-loop', '0'] + files_list + [output], verbose)

    @staticmethod
    def create(files_list, output, frames_per_second=3.0, verbose=False):
        process = GIF.create_async(files_list, output, frames_per_second, verbose)
        (out, err) = process.communicate()
        ret_code = process.returncode
        return out, err, ret_code


parser = argparse.ArgumentParser(description='Converts images to smaller size & creates gifs.')
parser.add_argument('fps', metavar='fpss', type=float, nargs='+',
                    help='list of frames per second for creating gifs')
parser.add_argument('-r', '--resize', type=int, metavar='percents',
                    help='resize ratio in percents to resize images before create gif.')
parser.add_argument('-s', '--max-size', type=float, metavar='max_size',
                    help='if passed, images will be resized to rich passed size.')
parser.add_argument('-p', '--prefix-of-input-files', metavar='prefix', default='',
                    help='prefix of input files to converting.')
parser.add_argument('-f', '--gif-name', metavar='name', default=None,
                    help='name for created gif.')
parser.add_argument('-o', '--output', metavar='output', default='',
                    help='output directory for created gif.')
parser.add_argument('-v', '--verbose',
                    help='increase verbosity.')
parser.add_argument('--synchronous',
                    help='execute synchronously.')
args = parser.parse_args()

print("Arguments %s" % args)

if args.max_size is not None and args.resize is not None:
    print("provided both --max-size (-s) and --resize (-r) options, they are exclusive, provide only one")
    exit(1)

wd = os.getcwd()
jpgs = [jpg for jpg in os.listdir(wd) if jpg.lower().endswith(".jpg") or jpg.lower().endswith(".jpeg")]
pngs = [png for png in os.listdir(wd) if png.lower().endswith(".png")]
imgs = None

if len(jpgs) != 0 and len(pngs) != 0:
    answer = input('In %s exists both jpg files and png, which You want use? [png/jpg]: ' % wd)
    if answer == 'jpg':
        imgs = jpgs
    elif answer == 'png':
        imgs = pngs
    else:
        print("Bad response, exiting.")
        exit(1)
elif len(jpgs) != 0:
    imgs = jpgs
elif len(pngs) != 0:
    imgs = pngs
else:
    print("No images in %s, exiting." % wd)
    exit(0)

imgs = [img for img in imgs if img.startswith(args.prefix_of_input_files)]


def average_of_file_size(files, verbose=False):
    """
    :return: average size of files, in MB
    :rtype int
    """
    sizes = [os.path.getsize(fil) for fil in files]
    size_avg = sum(sizes) * 1.0 / len(sizes) / 1024 / 1024
    if verbose:
        print("File size average: %.4fMB, calculated from sizes: %s" % (size_avg, sizes))
    return size_avg


imgs.sort()

if args.gif_name is None:
    name = input('Provide name of gif: ')
else:
    name = args.gif_name

fpss = args.fps
resize = args.resize
if resize is None:
    resize = args.max_size
    if resize is not None:
        resize = int(resize * 100 / average_of_file_size(imgs, args.verbose) + 6)


def gif_create(data):
    (images, output_prefix, name, verbose, fps) = data
    return GIF.create(images, '%s%s-%sfps.gif' % (output_prefix, name, fps), float(fps), verbose)


if args.synchronous:
    if resize is not None:
        imgs = [f[0] for f in map(lambda f_n: CONVERT.convert_percent(resize, f_n, args.verbose), imgs)]
else:
    if resize is not None:
        processes = map(lambda f_n: CONVERT.convert_percent_async(resize, f_n, args.verbose), imgs)
        imgs = []
        for (res, proc) in processes:
            proc.wait()
            imgs.append(res)

output_prefix = ""
if args.output is not None and len(args.output) > 0:
    output_prefix = args.output
    if not output_prefix.endswith('/'):
        output_prefix += "/"

if len(fpss) == 1:
    GIF.create(imgs, '%s%s.gif' % (output_prefix, name), int(fpss[0]), verbose=args.verbose)
else:
    if args.synchronous:
        for fps in fpss:
            GIF.create(imgs, '%s%s-%sfps.gif' % (output_prefix, name, fps), float(fps), args.verbose)
    else:
        processes = [GIF.create_async(imgs, '%s%s-%sfps.gif' % (output_prefix, name, fps), float(fps), args.verbose)
                     for fps in fpss]
        [p.wait() for p in processes]
