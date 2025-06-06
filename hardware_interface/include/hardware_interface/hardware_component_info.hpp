// Copyright (c) 2021, Stogl Robotics Consulting UG (haftungsbeschränkt)
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//
// Author: Denis Stogl
//

#ifndef HARDWARE_INTERFACE__HARDWARE_COMPONENT_INFO_HPP_
#define HARDWARE_INTERFACE__HARDWARE_COMPONENT_INFO_HPP_

#include <memory>
#include <string>
#include <vector>

#include "rclcpp/time.hpp"
#include "rclcpp_lifecycle/state.hpp"

#include "hardware_interface/types/statistics_types.hpp"
namespace hardware_interface
{
struct HardwareComponentStatisticsData
{
  ros2_control::MovingAverageStatisticsData execution_time;
  ros2_control::MovingAverageStatisticsData periodicity;
};
/// Hardware Component Information
/**
 * This struct contains information about a given hardware component.
 */
struct HardwareComponentInfo
{
  /// Component name.
  std::string name;

  /// Component "classification": "actuator", "sensor" or "system"
  std::string type;

  /// Component group
  std::string group;

  /// Component pluginlib plugin name.
  std::string plugin_name;

  /// Component is async
  bool is_async;

  //// read/write rate
  unsigned int rw_rate;

  /// Component current state.
  rclcpp_lifecycle::State state;

  /// List of provided state interfaces by the component.
  std::vector<std::string> state_interfaces;

  /// List of provided command interfaces by the component.
  std::vector<std::string> command_interfaces;

  /// Read cycle statistics of the component.
  std::shared_ptr<HardwareComponentStatisticsData> read_statistics = nullptr;

  /// Write cycle statistics of the component.
  std::shared_ptr<HardwareComponentStatisticsData> write_statistics = nullptr;
};

}  // namespace hardware_interface
#endif  // HARDWARE_INTERFACE__HARDWARE_COMPONENT_INFO_HPP_
