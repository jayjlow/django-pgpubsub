import multiprocessing

from django.core.management import BaseCommand
from django.db import connection

from pgpubsub.listen import listen, start_listen_in_a_process


class Command(BaseCommand):
    help = 'Listen to the named postgres channel(s) for notifications.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--channels',
            type=str,
            dest='channels',
            nargs='+',
        )
        parser.add_argument(
            '--processes',
            type=int,
            dest='processes',
        )
        parser.add_argument(
            '--worker',
            action='store_true',
            dest='worker',
            default=False,
            help='Start a worker listener process.',
        )
        parser.add_argument(
            '--worker-start-method',
            type=str,
            dest='worker_start_method',
            default="spawn",
            help=(
                "A method ('spawn', 'fork') used to start a worker "
                "listener process. 'fork' is the quickest on POSIX systems but unsafe "
                "if other threads are started during django initialization and/or from "
                "the listener callbacks.",
            ),
        )
        parser.add_argument(
            '--autorestart-on-failure',
            action='store_true',
            dest='autorestart_on_failure',
            default=True,
            help='Automatically restart a worker listener process on a failure.',
        )
        parser.add_argument(
            '--recover',
            action='store_true',
            dest='recover',
            default=False,
            help='Process all stored notifications for selected channels.',
        )

    def handle(self, *args, **options):
        channel_names = options.get('channels')
        processes = options.get('processes') or 1
        recover = options.get('recover', False)
        worker = options.get('worker', False)
        worker_start_method = options.get('worker_start_method')
        autorestart_on_failure = options.get('autorestart_on_failure', True)
        if worker:
            listen(
                channel_names,
                recover,
                autorestart_on_failure,
                start_method=worker_start_method,
            )
        else:
            for i in range(processes):
                start_listen_in_a_process(
                    channel_names, recover,
                    autorestart_on_failure,
                    start_method=worker_start_method,
                    name=f'pgpubsub_process_{i}',
                )
