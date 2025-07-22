import logging

import click

import ckan.plugins.toolkit as tk
from ckan import model

from ckanext.datagovau.geoserver_utils import CONFIG_PUBLIC_URL, run_ingestor

log = logging.getLogger(__name__)


@click.group("geoserver-ingestor", short_help="Ingest spatial data")
@click.help_option("-h", "--help")
def geoserver_ingestor():
    pass


@geoserver_ingestor.command("ingest")
@click.option("-d", "--dataset", help="Get specific dataset", default=None)
@click.option(
    "-o",
    "--organization",
    help="Datasets of specific organization",
    default=False,
)
def geo_ingest(dataset, organization):
    query = model.Session.query(model.Package).filter_by(state="active", private=False)
    if organization:
        org = model.Group.get(organization)
        if not org:
            tk.error_shout(f"Organization {organization} not found")
            raise click.Abort

        query = query.filter(model.Package.owner_org == org.id)

    if dataset:
        query = query.filter(
            (model.Package.name == dataset) | (model.Package.id == dataset)
        )

    for dataset in query:
        run_ingestor(dataset.id)


# ONE TIME SCRIPT
# TODO: remove it before the next release(when spatialingestore deployed)
@geoserver_ingestor.command("rmv-old-geo-res")
def rmv_old_geo_res():
    q = model.Session.query(model.Resource).filter(
        model.Resource.url.ilike(tk.config[CONFIG_PUBLIC_URL] + "%"),
        model.Resource.state != "deleted",
    )
    user = tk.get_action("get_site_user")({"ignore_auth": True}, {})

    with click.progressbar(q, length=q.count()) as bar:
        for res in bar:
            bar.label = f"Removing {res.id}"
            tk.get_action("resource_delete")(
                {"user": user["name"]},
                {"id": res.id},
            )
