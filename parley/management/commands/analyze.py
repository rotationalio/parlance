# parley.management.commands.analyze
# Runs the metrics analytics commands and caches them on the model evaluations.
#
# Author:   Benjamin Bengfort <benjamin@rotational.io>
# Created:  Mon Oct 07 15:50:03 2024 -0500
#
# Copyright (C) 2024 Rotational Labs, Inc.
# For license information, see LICENSE
#
# ID: analyze.py [] benjamin@rotational.io $

"""
Runs the metrics analytics commands and caches them on the model evaluations.
"""

##########################################################################
## Imports
##########################################################################

from parley.models import ModelEvaluation, Sensitive

from parley.tasks import cache_metrics, evaluate_label_correct
from parley.tasks import evaluate_valid_output_type, evaluate_leaks_sensitive
from parley.tasks import evaluate_cyberjudge_label_correct, extract_cyberjudge_label

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    help = "Run metrics analytics tasks and cache them on model evaluations"

    def add_arguments(self, parser):
        parser.add_argument(
            "-C", "--cyberjudge", action="store_true",
            help="run the cyberjudge evaluations before metrics",
        )
        parser.add_argument(
            "-L", "--labels", action="store_true",
            help="run the simple label correctness evaluation before metrics"
        )
        parser.add_argument(
            "-O", "--output-type", action="store_true",
            help="evaluate output type format before metrics",
        )
        parser.add_argument(
            "-S", "--sensitive", action="store_true",
            help="evaluation sensitive leaks before metrics"
        )
        parser.add_argument(
            "-A", "--all", action="store_true",
            help="run the evaluation metrics across all model evaluations",
        )
        parser.add_argument(
            "-y", "--yes", action="store_true",
            help="do not prompt for input on the command line",
        )
        parser.add_argument(
            "-f", "--filter", type=str, metavar="name",
            help="filter the model evaluations to run based on evaluation name"
        )
        parser.add_argument(
            "model_evaluations", nargs="*", metavar="uuid",
            help="specify the model evaluation(s) to run analytics for"
        )
        return super().add_arguments(parser)

    def handle(self, *args, **opts):
        # Make sure the user doesn't shoot their thumb off.
        self.validate_input(*args, **opts)

        # Lookup the model evaluations specified by the user in the database
        model_evaluations = self.get_queryset(**opts)
        n_model_evals = model_evaluations.count()
        if n_model_evals == 0:
            raise CommandError("no model evaluations found for criteria")

        print(f"found {n_model_evals} model evaluations for criteria:")
        for me in model_evaluations:
            print(f"  - {str(me)}")

        # Check that the user wants to continue
        if not opts["yes"]:
            if not self.confirm("continue with analysis?"):
                self.stdout.write(
                    self.style.WARNING("canceled operation by user")
                )

        # Prepare pre-checks
        self._sensitive = None
        prechecks = self.prechecks(**opts)
        if len(prechecks) > 0:
            print(f"performing {len(prechecks)} prechecks on responses")

        for me in model_evaluations:
            # Perform any required pre-checks
            if len(prechecks) > 0:
                for response in me.responses():
                    for check in prechecks:
                        check(response)

            # Cache metrics for the evaluation
            cache_metrics(me)

        self.stdout.write(
            self.style.SUCCESS("successfully completed analysis")
        )

    def validate_input(self, *args, **opts):
        if opts["cyberjudge"] and opts["labels"]:
            raise CommandError("specify either cyberjudge or simple labeling")

        model_evaluations = opts["model_evaluations"]
        if len(model_evaluations) > 0 and opts["all"]:
            raise CommandError("specify either model evaluations or --all not both")

        if len(model_evaluations) > 0 and opts["filter"]:
            raise CommandError("specify either model evaluations or --filter not both")

        if opts["all"] and opts["filter"]:
            raise CommandError("specify either --all or --filter not both")

    def get_queryset(self, **opts):
        if opts["all"]:
            return ModelEvaluation.objects.all()

        if opts["filter"]:
            return ModelEvaluation.objects.filter(
                evaluation__name__icontains=opts["filter"]
            )

        if opts["model_evaluations"]:
            return ModelEvaluation.objects.filter(id__in=opts["model_evaluations"])

    def confirm(self, prompt):
        while True:
            result = input(f"{prompt} [Y/n] ").strip().lower()
            if result[0] == "y":
                return True

            if result[0] == "n":
                return False

    def prechecks(self, **opts):
        """
        Puts together the precheck functions.
        """
        prechecks = []
        precheck_funcs = (
            ("output_type", self.evaluate_output_type),
            ("sensitive", self.evaluate_sensitive),
            ("cyberjudge", self.evaluate_cyberjudge),
            ("labels", self.evaluate_labels),
        )

        # NOTE: it is assumed precheck_funcs is sorted by application order
        for name, fn in precheck_funcs:
            if opts[name]:
                prechecks.append(fn)

        return prechecks

    def evaluate_cyberjudge(self, response):
        extract_cyberjudge_label(response)
        evaluate_cyberjudge_label_correct(response)

    def evaluate_labels(self, response):
        evaluate_label_correct(response)

    def evaluate_output_type(self, response):
        evaluate_valid_output_type(response)

    def evaluate_sensitive(self, response):
        if self._sensitive is None:
            self._sensitive = list(Sensitive.objects.all())
        evaluate_leaks_sensitive(response, self._sensitive)
