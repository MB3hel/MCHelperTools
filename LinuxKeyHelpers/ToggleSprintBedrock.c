
#include <string.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>
#include <fcntl.h>
#include <libudev.h>
#include <libinput.h>
#include <poll.h>
#include <linux/uinput.h>

static struct uinput_setup usetup;
static int uifd;

static int stop = 0;

static int sprint_state = 0;

static int open_restricted(const char *path, int flags, void *user_data){
  int fd = open(path, flags);
  return fd < 0 ? -errno : fd;
}

static void close_restricted(int fd, void *user_data){
  close(fd);
}

const static struct libinput_interface interface = {
        .open_restricted = open_restricted,
        .close_restricted = close_restricted,
};

void handle_event(int, int);

static void sighandler(int signal, siginfo_t *siginfo, void *userdata){
    stop = 1;
}

int main(void){
    struct sigaction act;
    memset(&act, 0, sizeof(act));
    act.sa_sigaction = sighandler;
    act.sa_flags = SA_SIGINFO;
    sigaction(SIGINT, &act, NULL);

    uifd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);
    ioctl(uifd, UI_SET_EVBIT, EV_KEY);
    ioctl(uifd, UI_SET_KEYBIT, KEY_F9);
    memset(&usetup, 0, sizeof(usetup));
    usetup.id.bustype = BUS_USB;
    usetup.id.vendor = 0x0000; 
    usetup.id.product = 0x0000;
    strcpy(usetup.name, "Virtual Keyboard (ToggleSpringBedrock)");
    ioctl(uifd, UI_DEV_SETUP, &usetup);
    ioctl(uifd, UI_DEV_CREATE);

    struct libinput *li;
    struct udev *udev = udev_new();
    struct libinput_event *ev;
    li = libinput_udev_create_context(&interface, NULL, udev);
    libinput_udev_assign_seat(li, "seat0");
    libinput_dispatch(li);

    struct pollfd fds;
    fds.fd = libinput_get_fd(li);
    fds.events = POLLIN;
    fds.revents = 0;


    while(!stop){
        if(poll(&fds, 1, -1) <= -1)
            continue;
        libinput_dispatch(li);
        while((ev = libinput_get_event(li))){
            if(libinput_event_get_type(ev) == LIBINPUT_EVENT_KEYBOARD_KEY){
                struct libinput_event_keyboard *kbev = libinput_event_get_keyboard_event(ev);
                int kstate = libinput_event_keyboard_get_key_state(kbev);
                int kcode = libinput_event_keyboard_get_key(kbev);
                handle_event(kstate, kcode);
            }
            libinput_event_destroy(ev);
        }
    }
    libinput_unref(li);
    return 0;
}

void emit(int fd, int type, int code, int val){
   struct input_event ie;
   ie.type = type;
   ie.code = code;
   ie.value = val;
   ie.time.tv_sec = 0;
   ie.time.tv_usec = 0;
   write(fd, &ie, sizeof(ie));
}

void toggle_sprint(void){
    sprint_state = !sprint_state;

    if(sprint_state){
        emit(uifd, EV_KEY, KEY_F9, 1);
        emit(uifd, EV_SYN, SYN_REPORT, 0);
        printf("PRESS SPRINT\n");
    }else{
        emit(uifd, EV_KEY, KEY_F9, 0);
        emit(uifd, EV_SYN, SYN_REPORT, 0);
        printf("RELEASE SPRINT\n");
    }
}

void quick_release(void){

}

void handle_event(int kstate, int kcode){
    if(kstate == LIBINPUT_KEY_STATE_PRESSED){
        switch(kcode){
        case KEY_LEFTCTRL:
        case KEY_RIGHTCTRL:
            toggle_sprint();
            break;
        }
    }
}
