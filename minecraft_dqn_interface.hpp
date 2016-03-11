#ifndef __MINECRAFT_INTERFACE_H__
#define __MINECRAFT_INTERFACE_H__

#include <vector>
#include <memory>
#include <array>
#include <cstdint>

#include <Python.h>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

class MinecraftInterface {

public:

  MinecraftInterface(int argc, char *argv[], const std::string path);
  ~MinecraftInterface();

  /* use virtual otherwise linker will try to perform static linkage */
  virtual void initInterface(int argc, char *argv[], std::string path);
  virtual void initMethods();
  virtual void init(bool evaluate);
  virtual std::vector<int> get_action_set();
  // NOTE: the size of the array must match the pixels in the screen shot
  virtual std::shared_ptr<std::array<uint8_t, 7056> > get_screen_as_array();
  virtual cv::Mat get_screen();
  virtual cv::Mat get_screen(int gitr, int fitr);
  virtual double act(int action);
  virtual bool is_game_over();
  virtual void reset();

private:

  const char* moduleName = "interface";

  PyObject *module;
  PyObject *py_init, *py_get_action_set, *py_get_screen, *py_act, *py_is_game_over, *py_reset;

};

#endif
