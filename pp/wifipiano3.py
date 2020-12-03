"""
Wifipiano 3
"""
import subprocess

from common.log import logUtils as log
from helpers import mapsHelper
from objects import glob

latency = glob.stats["pp_calc_latency_seconds"].labels(game_mode="mania", relax="0")
excC = glob.stats["pp_calc_failures"].labels(game_mode="mania", relax="0")


class PianoError(Exception):
	pass


class WiFiPiano:
	__slots__ = ["beatmap", "score", "pp"]

	def __init__(self, beatmap_, score_):
		self.beatmap = beatmap_
		self.score = score_
		self.pp = 0
		self.getPP()

	def _runProcess(self):
		# Run with dotnet
		command = \
			"dotnet pp/maniapp-osu-tools/PerformanceCalculator/bin/Release/netcoreapp2.0/PerformanceCalculator.dll " \
			"performance {map} " \
			"-mode 3 " \
			"-score {score_.score} " \
			"-acc {acc} " \
			"-mods {score_.mods} ".format(
				map=self.mapPath,
				score_=self.score,
				acc=self.score.accuracy * 100
			)
		log.debug("wifipiano3 ~> running {}".format(command))
		process = subprocess.run(command, shell=True, stdout=subprocess.PIPE)

		# Get pp from output
		output = process.stdout.decode("utf-8", errors="ignore")
		log.debug("wifipiano3 ~> output: {}".format(output))
		lines = output.split("\n")
		found = False
		pp = 0.
		for line in lines:
			parts = [x.strip().lower() for x in line.split(":")]
			if parts[0] != "pp":
				continue
			found = True
			try:
				pp = float(parts[1])
			except ValueError:
				raise PianoError("Invalid 'pp' value (got '{}', expected a float)".format(parts[1]))
		if not found:
			raise PianoError("No 'pp' in PerformanceCalculator.dll output")
		log.debug("wifipiano3 ~> returned pp: {}".format(pp))
		return pp

	@latency.time()
	def getPP(self):
		try:
			# Reset pp
			self.pp = 0

			# Cache map
			mapsHelper.cacheMap(self.mapPath, self.beatmap)

			# Calculate pp
			self.pp = self._runProcess()
		except PianoError:
			log.warning("Invalid beatmap {}".format(self.beatmap.beatmapID))
			self.pp = 0
		finally:
			if self.pp == 0 and excC is not None:
				excC.inc()
			return self.pp

	@property
	def mapPath(self):
		return mapsHelper.cachedMapPath(self.beatmap.beatmapID)
