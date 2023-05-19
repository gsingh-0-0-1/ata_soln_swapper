import os
import sys
import subprocess

import argparse

import datetime
import pyuvdata

CP_CMDS = [
'sudo cp ./delays_b.txt.new %s/delays_b.txt',
'sudo cp ./delays_c.txt.new %s/delays_c.txt',
'sudo cp ./phases_b.txt.new %s/phases_b.txt',
'sudo cp ./phases_c.txt.new %s/phases_c.txt',
'sudo cp ./weights_b.bin.new %s/weights_b.bin',
'sudo cp ./weights_c.bin.new %s/weights_c.bin',
'sudo cp ./weights_b.txt %s/weights_b.txt',
'sudo cp ./weights_c.txt %s/weights_c.txt',
]

#SLACK_IMG_UPLOAD_CMDS = [
#['curl', '-F', 'file=@./observation.png', '-F', 'channels=$ATACHANNEL', '-H', '"Authorization: Bearer ${ATATOKEN}"', 'https://slack.com/api/files.upload'],
#['curl', '-F', 'file=@./calibration.png', '-F', 'channels=$ATACHANNEL', '-H', '"Authorization: Bearer ${ATATOKEN}"', 'https://slack.com/api/files.upload']
#]

#SLACK_CACHE_POST_CMD = ['curl', '-d', '"text=Solutions applied and cached in %s/%s"', '-d', '"channel=${ATACHANNEL}"', '-H', '"Authorization: Bearer ${ATATOKEN}"', '-X', 'POST', 'https://slack.com/api/chat.postMessage']

SOLUTIONS_DIR = '/opt/mnt/share'
CACHE_DIR = SOLUTIONS_DIR + '/solutions_cache'

CACHE_CMDS = [
'sudo cp '
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-rdir', '--readdir', action='store_true', help = 'Default option -- read and apply solutions from the current directory, which should be one produced by a calibration observation.')
    parser.add_argument('-rc', '--readcache', action='store_true', help = 'Select from cache and apply solutions')
    parser.add_argument('-sd', '--solutiondir', help = 'Select a solution from its directory save name')

    args = parser.parse_args()

    if args.readdir and args.readcache:
        print("Can not use both cache and directory options!")
    if not args.readdir and not args.readcache:
        print("Must either read from directory or from cache!")
    
    if args.readdir:
        for cmd in CP_CMDS:
            run_cmd = cmd % SOLUTIONS_DIR
            print("Running < %s >" % run_cmd)
            subprocess.run(run_cmd.split(" "))
        #for cmd in SLACK_IMG_UPLOAD_CMDS:
        #    print("Running", " ".join(cmd))
        #    subprocess.run(cmd)

        print("Caching solutions...")
        t = datetime.datetime.now()
        t = t.strftime("%Y-%m-%d-%H:%M:%S")
        
        # Now we need to get the name of the uvh5 files to read
        uvh5_files = [item for item in os.listdir("./") if ".uvh5" in item]
        freqs = []
        for f in uvh5_files:
            datafile = pyuvdata.UVData.from_file(f)
            freqarr = datafile.freq_array
            #we want the cfreq in MHz
            cfreq = round(freqarr.mean() / 1e6)
            freqs.append(str(cfreq))

        sol_name = t + "_" + "_".join(freqs)

        newdir = CACHE_DIR + "/" + sol_name
        subprocess.run(['/home/sonata/experimental/slackpost_new.bash', newdir])
        #SLACK_CACHE_POST_CMD[2] = SLACK_CACHE_POST_CMD[2] % (CACHE_DIR, t)
        #subprocess.run(SLACK_CACHE_POST_CMD)
        print("Creating cache directory < %s >" % newdir)
        subprocess.run(['sudo', 'mkdir', newdir])
        for cmd in CP_CMDS:
            run_cmd = cmd % newdir
            print("Running < %s >" % run_cmd)
            subprocess.run(run_cmd.split(" "))


    if args.readcache:
        l = [el for el in os.listdir(CACHE_DIR) if el[0] != '.']
        if len(l) == 0:
            print("No cached solutions found! Please run a calibration observation and apply solutions using the `-rdir` flag.")
        else:
            if args.solutiondir is None:
                print("No solution selected! Please run again and select a solution using the `-sd` option.")
            else:
                if args.solutiondir not in l:
                    print("Could not find solution! Available solutions are:")
                    for el in l:
                        print("\t%s" % el)
                else:
                    # now we can copy over files from the cache directly to the solutions directory
                    print("Applying solutions from cache %s" % args.solutiondir)
                    this_cache_dir = CACHE_DIR + "/" + args.solutiondir + "/*"
                    subprocess.call('sudo cp ' + this_cache_dir + " " + SOLUTIONS_DIR + "/", shell = True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    subprocess.run(['/home/sonata/experimental/slackpost_cac.bash', this_cache_dir])




