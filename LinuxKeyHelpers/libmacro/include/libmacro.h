#pragma once

#include <libinput.h>
#include <libudev.h>

enum LIBMACRO_EVENT_TYPE{
    LIBMACRO_EVENT_TYPE_KEYPRESS = 0,
    LIBMACRO_EVENT_TYPE_KEYRELEASE = 1,
    LIBMACRO_EVENT_TYPE_MOUSEPRESS = 2,
    LIBMACRO_EVENT_TYPE_MOUSERELEASE = 3,
    LIBMACRO_EVENT_TYPE_MOUSESCROLL_VERTICAL = 4,
    LIBMACRO_EVENT_TYPE_MOUSESCROLL_HORIZONTAL
};

typedef struct{
    struct libinput_interface libinput_interface;
    struct libinput *libinput;
    struct udev *udev;
} libmacro_context_t;

typedef struct{
    int event_type;
    int event_value;
} libmacro_event_t;

// Returns NULL on failure
libmacro_context_t *libmacro_init(void);

// Cleanup context created by libmacro_init
void libmacro_deinit(libmacro_context_t *context);

libmacro_event_t libmacro_wait_for_event(libmacro_context_t *context);
