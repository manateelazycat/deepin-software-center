/* Copyright (C) 2011 Deepin, Inc.
*                2011 Wang Yong
*
* Author:     Wang Yong <lazycat.manatee@gmail.com>
* Maintainer: Wang Yong <lazycat.manatee@gmail.com>
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/* Compile with command:
 *     gcc browser.c `pkg-config --cflags --libs gtk+-2.0 webkit-1.0` */

#include <stdlib.h>
#include <string.h>
#include <glib.h>
#include <gtk/gtk.h>
#include <webkit/webkit.h>
#include <libsoup/soup.h>
#include <Python.h>
#include "pygobject.h"

static WebKitWebView* browser_new(char uri[], char cookie_file[]) {
     GtkWidget *web_view = webkit_web_view_new();
     SoupSession *session = webkit_get_default_session();
     SoupCookieJar *cookie_jar = soup_cookie_jar_text_new(cookie_file, FALSE);
     soup_session_add_feature(session, SOUP_SESSION_FEATURE(cookie_jar));

     webkit_web_view_load_uri(WEBKIT_WEB_VIEW(web_view), uri);
     
     return WEBKIT_WEB_VIEW(web_view);
}

static PyObject* dsc_browser_new(PyObject *self, PyObject *args);

static PyMethodDef dsc_browser_methods[] = {
     {"browser_new", (PyCFunction)dsc_browser_new, METH_VARARGS,
      "Create WebKit browser with cookie support."},
     {NULL, NULL, 0, NULL}
};

static PyObject* dsc_browser_new(PyObject *self, PyObject *args) {
     char *uri;
     char *cookie_file;
     WebKitWebView *browser;
     
     if (!PyArg_ParseTuple(args, "ss", &uri, &cookie_file)) {
          return NULL;
     }
     
     browser = browser_new(uri, cookie_file);
     
     return pygobject_new((GObject *)browser);
}

PyMODINIT_FUNC initdsc_browser(void) {
     PyObject *m;

     /* This is necessary step for Python binding, otherwise got sefault error */
     init_pygobject();
     
     m = Py_InitModule("dsc_browser", dsc_browser_methods);

     if (!m) {
          return;
     }
}
