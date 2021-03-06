# Copyright (C) 2013 Linaro Limited
#
# Author: Senthil Kumaran <senthil.kumaran@linaro.org>
#
# This file is part of LAVA Scheduler.
#
# LAVA Scheduler is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License version 3 as
# published by the Free Software Foundation
#
# LAVA Scheduler is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Scheduler.  If not, see <http://www.gnu.org/licenses/>.

import logging

from twisted.application.service import Service
from twisted.internet.task import LoopingCall

from lava_scheduler_daemon.job import JobRunner, catchall_errback


class JobQueue(Service):

    def __init__(self, source, dispatcher, reactor, daemon_options):
        self.logger = logging.getLogger(__name__ + '.JobQueue')
        self.source = source
        self.dispatcher = dispatcher
        self.reactor = reactor
        self.daemon_options = daemon_options
        self._check_job_call = LoopingCall(self._checkJobs)
        self._check_job_call.clock = reactor

    def _checkJobs(self):

        self.logger.debug("Refreshing jobs")
        return self.source.getJobList().addCallback(
            self._startJobs).addErrback(catchall_errback(self.logger))

    def _startJobs(self, jobs):
        for job in jobs:
            new_job = JobRunner(self.source, job, self.dispatcher,
                                self.reactor, self.daemon_options)
            self.logger.info("Starting Job: %d ", job.id)

            new_job.start()

    def startService(self):
        self.logger.info("\n\nLAVA Scheduler starting\n\n")
        self._check_job_call.start(20)

    def stopService(self):
        self._check_job_call.stop()
        return None
