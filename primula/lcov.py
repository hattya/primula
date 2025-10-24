#
# primula.lcov
#
#   Copyright (c) 2025 Akinori Hattori <hattya@gmail.com>
#
#   SPDX-License-Identifier: Apache-2.0
#

from __future__ import annotations
from collections.abc import Iterable
import sys
from typing import IO

import coverage.control
import coverage.report
import coverage.results as coverage_results

from . import core
from ._typing import MorF


__all__ = ['LCOVReporter']


class LCOVReporter:

    report_type = "LCOV report"

    def __init__(self, coverage: coverage.control.Coverage, profile: core.Profile | None) -> None:
        self.coverage = coverage
        self.config = coverage.config
        self.total = coverage_results.Numbers(self.config.precision)
        self.profile = profile

    def report(self, morfs: Iterable[MorF] | None, outfile: IO[str]) -> float:
        self.coverage.get_data()
        outfile = outfile or sys.stdout
        for fr, analysis in sorted(coverage.report.get_analysis_to_report(self.coverage, morfs),
                                   key=lambda v: v[0].relative_filename()):
            outfile.write('TN:\n')
            outfile.write(f'SF:{fr.relative_filename()}\n')
            if self.profile:
                s = self.profile.scripts[fr.filename]
                outfile.writelines(f'DA:{i},{s.lines[i-1].count}\n' for i in analysis.statements)
            else:
                outfile.writelines(f'DA:{i},{int(i not in analysis.missing)}\n' for i in analysis.statements)
            outfile.write(f'LF:{analysis.numbers.n_statements}\n')
            outfile.write(f'LH:{analysis.numbers.n_executed}\n')
            outfile.write('end_of_record\n')
            self.total += analysis.numbers
        return self.total.n_statements and self.total.pc_covered
