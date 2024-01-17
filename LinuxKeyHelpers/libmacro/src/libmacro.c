
#include <libmacro.h>
#include <fcntl.h>
#include <unistd.h>

////////////////////////////////////////////////////////////////////////////////
/// libinput_interface implementation
////////////////////////////////////////////////////////////////////////////////

int libmacro_open_restricted(const char *path, int flags, void *user_data){
    return open(path, flags);
}

void libmacro_close_restricted(int fd, void *user_data){
    close(fd);
}

////////////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////////////
/// libmacro API
////////////////////////////////////////////////////////////////////////////////

libmacro_context_t *libmacro_init(void){
    libmacro_context_t *context = malloc(sizeof(libmacro_context_t));
    context->udev = udev_new();
    context->libinput_interface.open_restricted = libmacro_open_restricted;
    context->libinput_interface.close_restricted = libmacro_close_restricted;
    context->libinput = libinput_udev_create_context(&context->libinput_interface, NULL, context->udev);
    int rc = libinput_udev_assign_seat(context->libinput, "seat0");
    if(rc != 0){
        free(context);
        return NULL;
    }
}

void libmacro_deinit(libmacro_context_t *context){
    if(context != NULL){
        while(libinput_unref(context->libinput));
        udev_unref(context->udev);
        free(context);
    }
}

libmacro_event_t libmacro_wait_for_event(libmacro_context_t *context){
    while(1){
        libinput_dispatch(context->libinput);
        struct libinput_event *ev = libinput_get_event(context->libinput);
        if(ev == NULL)
            continue;
        
        libmacro_event_t macroev;

        switch(libinput_event_get_type(ev)){
        case LIBINPUT_EVENT_POINTER_BUTTON:
            // Mouse clicks (left, right, middle, side buttons)
            struct libinput_event_pointer *pbev = libinput_event_get_pointer_event(ev);
            int button = libinput_event_pointer_get_button(pbev);
            if(libinput_event_pointer_get_button_state(pbev)){
                // Button pressed
                macroev.event_type = LIBMACRO_EVENT_TYPE_MOUSEPRESS;
                macroev.event_value = button;
            }else{
                // Button released
                macroev.event_type = LIBMACRO_EVENT_TYPE_MOUSERELEASE;
                macroev.event_value = button;
            }
            break;
        case LIBINPUT_EVENT_POINTER_SCROLL_WHEEL:
            // Mouse wheel
            struct libinput_event_pointer *psev = libinput_event_get_pointer_event(ev);
            if(libinput_event_pointer_has_axis(psev, LIBINPUT_POINTER_AXIS_SCROLL_VERTICAL)){
                macroev.event_type = LIBMACRO_EVENT_TYPE_MOUSESCROLL_VERTICAL;
                macroev.event_value = libinput_event_pointer_get_axis_value(psev, LIBINPUT_POINTER_AXIS_SCROLL_VERTICAL);
            }else if(libinput_event_pointer_has_axis(psev, LIBINPUT_POINTER_AXIS_SCROLL_HORIZONTAL)){
                macroev.event_type = LIBMACRO_EVENT_TYPE_MOUSESCROLL_HORIZONTAL;
                macroev.event_value = libinput_event_pointer_get_axis_value(psev, LIBINPUT_POINTER_AXIS_SCROLL_HORIZONTAL);
            }
            break;
        case LIBINPUT_EVENT_KEYBOARD_KEY:
            // Keyboard keys
            struct libinput_event_keyboard *kev = libinput_event_get_keyboard_event(ev);
            int key = libinput_event_keyboard_get_key(kev);
            if(libinput_event_keyboard_get_key_state(kev)){
                // Button pressed
                macroev.event_type = LIBMACRO_EVENT_TYPE_KEYPRESS;
                macroev.event_value = key;
            }else{
                // Button released
                macroev.event_type = LIBMACRO_EVENT_TYPE_KEYRELEASE;
                macroev.event_value = key;
            }
            break;
        default:
            // The received event is not one we care about.
            libinput_event_destroy(ev);
            continue;
        }
        libinput_event_destroy(ev);

        // Received an event that should be handled by macro scripts
        return macroev;
    }
}

////////////////////////////////////////////////////////////////////////////////
