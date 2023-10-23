import gym
from verbal_gym.llm.gpt_models import GPT
from verbal_gym.llm import make_llm
from verbal_gym.agents.basic_agent import BasicAgent
from verbal_gym.agents.random_agent import RandomAgent
from verbal_gym.utils.utils import evaluate_agent, set_seed
from verbal_gym.utils.misc_utils import print_color


def main(args):

    n_episodes = args.n_episodes
    horizon = args.horizon

    # Create the environment
    env = gym.make(args.env_name)
    set_seed(args.seed, env)

    n_actions = env.action_space.n if isinstance(env.action_space, gym.spaces.Discrete) else None
    action_name = 'Action'
    if any([name in args.env_name for name in ('Haiku', 'Tanka', 'LineSyllableConstrainedPoem', 'SyllableConstrainedPoem')]):
        action_name = 'Poem'

    # TODO should save the stdout

    if n_actions is not None:  # finite action, so we can test RandomAgent and FullInformationAgent as well.
        # Random agent
        random_agent = RandomAgent(n_actions)
        scores = evaluate_agent(random_agent, env, horizon=horizon, n_episodes=n_episodes, n_workers=args.n_workers)
        print_color('Random agent: mean score {:.2f}, std {:.2f}'.format(scores.mean(), scores.std()), 'red')

        from verbal_gym.envs.env_wrapper import FullInformationWrapper
        from verbal_gym.agents.basic_agent import FullInformationAgent
        env = FullInformationWrapper(env)

        # Full information agent
        system_prompt = FullInformationAgent.system_prompt
        llm = GPT(system_prompt)
        gpt_agent = FullInformationAgent(llm,
                                         n_actions=n_actions,
                                         verbose=args.verbose)

        scores = evaluate_agent(gpt_agent,
                                env,
                                horizon=horizon,
                                n_episodes=n_episodes,
                                n_workers=args.n_workers,
                                return_full_information=True)
        print_color('Oracle LLM agent: mean score {:.2f}, std {:.2f}'.format(scores.mean(), scores.std()), 'red')


def get_parser():

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--n_episodes', type=int, default=10)
    parser.add_argument('--horizon', type=int, default=10)
    parser.add_argument('--env_name',type=str, default='verbal-BanditTenArmedRandomRandom-v0')  #'verbal-Haiku-v0'
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--n_workers', type=int, default=1)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--model', type=str, default='azure:gpt-35-turbo')
    return parser


if __name__ == '__main__':
    parser = get_parser()
    main(parser.parse_args())