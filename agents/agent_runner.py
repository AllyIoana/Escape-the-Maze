import random_agent.random_agent
import dfs_agent.dfs_agent
import view_learning_agent.view_learning_agent
import view_learning_agent_v2.view_learning_agent_v2
import view_learning_agent_v3.view_learning_agent_v3
import a_star_agent.a_star_agent
import bfs_agent.bfs_agent
import threading
SERVER_URL = "http://localhost:8000"

def solve_random():
    agent = random_agent.random_agent.RandomAgent(SERVER_URL)
    agent.solve()

def solve_dfs():
    agent = dfs_agent.dfs_agent.DFSAgent(SERVER_URL)
    agent.solve()

def solve_view_learning(version = 1):
    if version == 1:
        agent = view_learning_agent.view_learning_agent.ViewLearningAgent(SERVER_URL, mode="solve")
        agent.solve()
    elif version == 2:
        agent = view_learning_agent_v2.view_learning_agent_v2.ViewLearningAgentV2(SERVER_URL, mode="solve")
        agent.solve()
    else:
        agent = view_learning_agent_v3.view_learning_agent_v3.ViewLearningAgentV3(SERVER_URL, mode="solve")
        agent.solve()

def train_view_learning(version = 1):
    if version == 1:
        agent = view_learning_agent.view_learning_agent.ViewLearningAgent(SERVER_URL, mode="train")
        agent.create_training_data()
        agent.train()
    elif version == 2:
        agent = view_learning_agent_v2.view_learning_agent_v2.ViewLearningAgentV2(SERVER_URL, mode="train")
        agent.create_training_data()
        agent.train()
    else:
        agent = view_learning_agent_v3.view_learning_agent_v3.ViewLearningAgentV3(SERVER_URL, mode="train")
        agent.create_training_data()
        agent.train()

def solve_bfs():
    agent = bfs_agent.bfs_agent.BFSAgent(SERVER_URL)
    agent.solve()

def solve_a_star():
    agent = a_star_agent.a_star_agent.AStarAgent(SERVER_URL)
    agent.solve()

if __name__ == '__main__':
    random_thread = threading.Thread(target=solve_random)
    dfs_thread = threading.Thread(target=solve_dfs)
    view_learning_thread = threading.Thread(target=solve_view_learning, args=[3])
    bfs_thread = threading.Thread(target=solve_bfs)
    a_star_thread = threading.Thread(target=solve_a_star)

    random_thread.daemon = True
    dfs_thread.daemon = True
    view_learning_thread.daemon = True
    bfs_thread.daemon = True
    a_star_thread.daemon = True

    # random_thread.start()
    # dfs_thread.start()
    view_learning_thread.start()
    # bfs_thread.start()
    # a_star_thread.start()

    # random_thread.join()
    # dfs_thread.join()
    view_learning_thread.join()
    # bfs_thread.join()
    # a_star_thread.join()