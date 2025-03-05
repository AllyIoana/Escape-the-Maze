# Introduction

This document provides a testing report for the different components of our project. The report includes feedback on the Random Maze Generator, Semi-Random Maze Generator, Viewer, Server, and Agents. The purpose of this report is to identify areas for improvement and optimization in the project and provide suggestions for enhancing the user experience and performance.

With the effort we put into finding bugs for the second milestone, we have found many bugs and fixed them. However, there are still some areas that need further optimization and improvement. 

# Testing Methodology

For the third milestone, we now have automated tests for the server and the generation of the mazes. For the viewer and the agents, as they are GUI components, we have
manual tests. The testing was performed manually by running the different components of the project and interacting with them to identify any issues or areas for improvement. The testing process involved generating mazes, solving mazes, and visualizing the maze layouts using the viewer. The server and agents were also tested to ensure they functioned correctly and interacted with the other components as expected.

# Random Maze Generator

Luckily, for the Random Maze Generator, we have already fixed most of the issues that were found during the second milestone. The one issue we found was that the maze generator is very
inefficient when generating larger mazes. For this, Alexandra investigated the issue and found the problem. The issue was that the algorithm was not optimized for larger mazes. She then optimized the algorithm and now the Random Maze Generator is more efficient when generating larger mazes.

The automated tests verify that the maze is generated correctly and that the maze is solvable. The tests also verify that the maze is generated within a reasonable time frame. Also, the tests verify that the maze is generated with the correct dimensions and that the maze generator takes into account all variables when generating the maze.

# Semi-Random Maze Generator

Here, we don't have any issues with the Semi-Random Maze Generator. The performance of the Semi-Random Maze Generator is better than the Random Maze Generator, especially when generating larger mazes. The Semi-Random Maze Generator is more efficient due to its deterministic nature.

The automated tests here aren't as extensive as the ones for the Random Maze Generator, but they still verify that the maze is generated correctly and that the maze is solvable. The tests also verify that the maze is generated within a reasonable time frame. Also, the tests verify that the maze is generated with the correct dimensions.

# File Input Maze Generator

Same here, most of the issues were found and fixed during the second milestone. The one issue we found was that this component throws an exception in a very specific case that we missed
when the algorithm was implemented. Vladi fixed this issue by adding a check for this specific case, and now the File Input Maze Generator works as expected.

In the automated tests, we used this component as an extra check for the other tests, as it's the component we trust to verify if a maze is correct or not.

# Viewer

Here we have a few issues that we found during testing. The first issue is that the viewer hogs the server with requests for agents when no agents are present. This was reported to Oana
and she has fixed this issue. Another issue was when agents travel through the portal, the viewer doesn't display the agents' paths correctly. This was also reported to Oana and she has fixed this issue.

The manual tests verify that the viewer displays the maze correctly and that the viewer displays the agents' paths correctly. The manual testing also verifies how it handles different actions such as resizing and other interactions, and the interaction with the server and the agents.

# Server

For the server, we have automated tests that verify that the server can handle multiple clients simultaneously and that the communication between the server and clients is smooth and responsive. Also, we verify for every relevant endpoint that the server returns the correct response and that the server handles the requests correctly.

Manual testing here is done with Postman, where we test the endpoints and see if they return the correct response. We also test the server with the viewer and the agents to see how
they interact with the server.

# Agents

Here, several issues were found and fixed in the last sprints, so we don't have any issues with the agents. Now, the AI agent has been trained to solve the maze using a custom algorithm
and we have optimized the agent to be more efficient when solving the maze.