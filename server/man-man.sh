#!/bin/bash -

################################################################################
# 
# manman is the MANdox MANager, a script that allows you to start or stop
# the mandox server as well as query the status of it.
#
# Usage: ./manan.sh start | stop | status
#
#

MAN_LOG=mandox.log
MANDOX_PID=mandox.pid

function usage() {
	printf "Usage: %s start | stop | status\n" $0
}

function start_mandox() {
	nohup python mandox.py > $1 &> $1 &
	echo $! > $MANDOX_PID
}

function stop_mandox() {
	
	# try to find the PID and kill the server ...
	if [ -f $MANDOX_PID ]; then
		if kill -0 `cat $MANDOX_PID` > /dev/null 2>&1; then
			echo 'Shutting down mandox server'
			kill `cat $MANDOX_PID`
			rm $MANDOX_PID
		fi
	fi
	
	# ... as well as clean up the nohup stuff
	if [ -f nohup.out ]; then
		rm nohup.out
	fi
}

function mandox_running() {
	case `uname` in
		Linux|AIX) PS_ARGS='-ewwo pid,args'   ;;
		SunOS)     PS_ARGS='-eo pid,args'     ;;
		*BSD)      PS_ARGS='axwwo pid,args'   ;;
		Darwin)    PS_ARGS='Awwo pid,command' ;;
	esac

	if ps $PS_ARGS | grep -q '[p]ython mandox' ; then
		echo 'Yes, mandox server is running. See details in' $MAN_LOG
	else
		echo 'No, mandox server is not running.'
	fi
}

# Main script
case $1 in
 start )  start_mandox $MAN_LOG ;;
 stop )   stop_mandox ;;
 status ) mandox_running ;;
 * )      usage ; exit 1 ; ;;
esac


