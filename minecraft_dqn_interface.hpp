#ifndef __INTERFACE_H__
#define __INTERFACE_H__

#include <vector>

#include <Python.h>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

class Interface {

public:

  Interface(int argc, char *argv[], std::string path);
  ~Interface();

  /* use virtual otherwise linker will try to perform static linkage */
  virtual void initInterface(int argc, char *argv[], std::string path);
  virtual void initMethods();
  virtual void init();
  virtual std::vector<int> get_action_set();
  virtual cv::Mat get_screen();
  virtual cv::Mat get_screen(int gitr, int fitr);
  virtual int act(int action);
  virtual bool is_game_over();
  virtual void reset();

private:

  const char* moduleName = "interface";

  PyObject *module;
  PyObject *py_init, *py_get_action_set, *py_get_screen, *py_act, *py_is_game_over, *py_reset;

};

#endif
