#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#define ERR(...) fprintf(stderr, __VA_ARGS__); exit(-1);
#define PROG "/usr/bin/add_vpn_user.sh"

int main(int argc, char **argv)
{
	if (argc != 2) {
		ERR("usage: %s [1|2]\n", argv[0]);
	}

	if (strlen(argv[1]) != 1) {
		ERR("usage: %s [1|2]\n", argv[0]);
	}

	if (argv[1][0] != '1' && argv[1][0] != '2') {
		ERR("usage: %s [1|2]\n", argv[0]);
	}

	//ok we've validated input is sane, set our uid and do the work
	char *environ[] = { "PATH=/usr/bin:/usr/sbin:/bin:/sbin", NULL };
	char *args[] = { PROG, argv[1], NULL };

	setreuid(geteuid(), geteuid());
	errno = 0;

	//redirect stdout and stderr to /dev/null so we don't leak any output
        int fd = open("/dev/null", O_WRONLY);
        if (fd == -1) {
                ERR("open failed\n");
        }
        if (dup2(fd, STDOUT_FILENO) == -1) {
                ERR("dup2 failed\n");
                exit(-1);
        }
        if (dup2(fd, STDERR_FILENO) == -1) {
                ERR("dup2 failed\n");
                exit(-1);
        }

	execve(PROG, args, environ);
	return -1;
}
