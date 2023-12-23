import argparse
import sys
import greenstalk
from loguru import logger
from greenstalk import Client as BeanstalkClient


def main():
    # Configure loguru to log to stdout
    logger.remove()  # Remove default stderr handler
    logger.add(sys.stdout, format="{message}")

    parser = argparse.ArgumentParser(prog='pulpo-beanstalk-cli', description='Provides a set of common beanstalk utilities')
    parser.add_argument('command')
    parser.add_argument('--server', '-s', dest='host', default='127.0.0.1', help='beanstalkd host/server', type=str)
    parser.add_argument('--port', '-p', dest='port', default=11300, help='beanstalkd port', type=int)
    parser.add_argument('--encoding', '-e', dest='encoding', default='utf-8', help='encoding', type=str)
    parser.add_argument('--tube', '-t', dest='tube', default='default', help='beanstalkd tube', type=str)
    parser.add_argument('--id', dest='job_id', help='job id (for peek)', type=int)
    parser.add_argument('--put.body', '--body', dest='body', help='when performing `put`, body of message', type=str)
    parser.add_argument('--put.priority', '--priority', dest='priority', default=5, help='when performing `put`, priority of message', type=int)
    parser.add_argument('--put.delay', '--delay', dest='delay', default=0, help='when performing `put`, delay of message in seconds', type=int)
    parser.add_argument('--put.ttr', '--ttr', dest='ttr', default=0, help='when performing `put`, ttr in seconds', type=int)

    args = parser.parse_args()

    address = (args.host, args.port)
    client = BeanstalkClient(address=address, encoding=args.encoding, watch=args.tube, use=args.tube)

    match args.command:
        case 'pop':
            pop(client=client)
        case 'peek':
            peek(client=client, job_id=args.job_id)
        case 'delete':
            delete(client=client, job_id=args.job_id)
        case 'put':
            put(client=client, body=args.body, priority=args.priority, delay=args.delay, ttr=args.delay)
        case _:
            raise Exception(f'invalid command {args.command}')

    return 0


def pop(client: BeanstalkClient):
    try:
        job = client.reserve(timeout=0)
        client.delete(job)
        logger.info(f'pop: {job.id=} \n{job.body}')
    except greenstalk.TimedOutError:
        logger.info('no message available')


def peek(client: BeanstalkClient, job_id: int):
    if not job_id:
        raise Exception(f'invalid job id {job_id}')

    job = client.peek(id=job_id)
    logger.info(f'peek: {job.id=} \n{job.body}')


def put(client: BeanstalkClient, body: str, priority: int, delay: int, ttr):
    job_id = client.put(body=body, priority=priority, delay=delay, ttr=ttr)
    logger.info(f'put: {job_id=}')


def delete(client: BeanstalkClient, job_id: int):
    client.delete(job=job_id)
    logger.info(f'delete: {job_id=}')


if __name__ == '__main__':
    main()
