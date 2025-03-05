# Introduction

This document provides a testing report for the different components of the maze generation and solving project. The report includes feedback on the Random Maze Generator, Semi-Random Maze Generator, Viewer, Server, and Agents. The purpose of this report is to identify areas for improvement and optimization in the project and provide suggestions for enhancing the user experience and performance.

Most of the issues found during testing have been solved, and the project is now in a better state than before. However, there are still some areas that need further optimization and improvement. 

# Testing Methodology

The testing was performed manually by running the different components of the project and interacting with them to identify any issues or areas for improvement. The testing process involved generating mazes, solving mazes, and visualizing the maze layouts using the viewer. The server and agents were also tested to ensure that they functioned correctly and interacted with the other components as expected.

# Testing Report: Random Maze Generator
The current implementation of the maze generator has some areas that could be improved for better usability and performance.

Another suggestion is to modify the output so that the success or failure message, along with any key details, is printed only once at the end of the execution. This would make the output more concise and less cluttered during the testing process. (*Solved*)

The ability to specify the size, seed and threshold of the maze as a command-line argument would be a useful feature. It would allow for more flexibility and control over the generated maze, especially when testing different configurations. (*Solved*)

For testing purposes, it would be beneficial to introduce an argument, such as --test, which would disable the grayscale mode when generating the maze. This would help in distinguishing between different tiles more easily during testing and debugging. (*Solved*)

Lastly, while the maze generator works fine, the performance could be improved, especially when generating larger mazes. Optimizations might be needed to handle bigger mazes or more complex generation algorithms efficiently.

# Testing Report: Semi-Random Maze Generator

The same suggestions for the Random Maze Generator apply to the Semi-Random Maze Generator as well. The ability to specify the size, seed, and threshold as command-line arguments would be beneficial for testing and debugging purposes. (*Solved*)

At first, the Semi-Random Maze Generator seems to be more efficient due to its deterministic nature, but it still has room for improvement in terms of usability and performance.
However, the performance of the Semi-Random Maze Generator is better than the Random Maze Generator, especially when generating larger mazes.

# Testing Report: Viewer

The maze viewer functions quite well overall, with smooth movement and accurate rendering of tiles. I am satisfied with how it handles different actions such as resizing and other interactions—everything operates smoothly.

However, there are some limitations and areas for improvement:

First, the viewer does not support mouse drag functionality for moving around the maze. It would be useful if users could click and drag to navigate the maze, providing a more intuitive way to explore the layout. (*Solved*)

Additionally, the mouse wheel for scrolling up or down does not seem to work as expected. Implementing mouse wheel support for zooming in and out could significantly enhance the navigation experience. (*Solved*)

Currently, zooming is controlled only with the keyboard shortcuts Ctrl + and Ctrl -, but there is a specific behavior to note: zooming in with Ctrl + only works when using the plus key on the right side of the numpad. This limitation could be confusing for users who are used to the standard plus sign on the main keyboard. (*Solved*)

The zoom itself functions, but there is a slight inconsistency in how the zoom speed behaves. When zooming out (getting farther from the maze), the zoom happens quickly, whereas zooming in (getting closer to the maze) is quite slow. Adjusting the zoom speed to be more consistent or slower for both directions would improve the overall user experience. (*Solved*)

Currently, when the viewer starts, it hogs the server with requests for agents, when no agents are present. This could be optimized by only requesting agent information when agents are present in the maze. (TODO)

The viewer is also able to display the agents' paths, which is a useful feature for visualizing the search algorithms. This functionality works really well, I am very satisfied with it.

# Testing Report: Server

The server implementation is robust and reliable, handling multiple clients and requests effectively. The server can handle multiple clients simultaneously, and the communication between the server and clients is smooth and responsive.

The server uses FastAPI, which provides a clean and efficient way to create APIs. The endpoints are well-organized and easy to understand, making it simple to interact with the server programmatically.

The server also supports multiple endpoints for different functionalities, such as generating mazes, solving mazes, and viewing mazes. This modularity allows for easy extension and customization of the server's capabilities.

One suggestion for improvement is to add more error handling and validation to the server endpoints. This would help prevent unexpected errors and provide better feedback to clients when something goes wrong. (*Solved*)

There were some issues with the server's moves endpoint, where some exceptions were not handled correctly, leading to unexpected behavior. Adding more robust error handling and validation would help address these issues. (*Solved*)

Overall, the server implementation is solid and performs well, providing a reliable backend for the maze generation and solving functionalities.

# Testing Report: Agents

The agent implementation is well-structured and provides a flexible framework for different types of agents. The agents can navigate the maze efficiently and find the optimal path to the goal.

The random agent performs adequately, exploring the maze in a random manner and eventually reaching the goal. The random agent is a good baseline for comparison with more advanced agents. 

Here, some other issues were found where multiple exceptions were not handled correctly, leading to unexpected behavior. (*Solved*)

The DFS agent is currently very slow and inefficient, especially for larger mazes. Optimizations are needed to improve the performance of the DFS agent and make it more competitive with other search algorithms. (TODO)

For the current milestone, I am satisfied with the agent implementations, but there is still room for improvement in terms of performance and efficiency.

# Conclusion

Overall, testing the different components of the maze generation and solving manually has proven to be effective in identifying areas for improvement and optimization. The feedback provided in this report will help guide the development process and ensure that the final product meets the desired quality standards.