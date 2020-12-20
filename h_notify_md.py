import os, sys
sys.path.append("./hypothesis") # make submodule "visible"
import dateutil.parser
import logging
from mdutils.mdutils import MdUtils
from h_notify import Notifier

date_format = "%Y-%m-%d"
file_log_err_level = logging.ERROR # logging.ERROR is recommended


def init_logger(name=None, level=None, custom_logging=None):
    logger_name = name or 'h_notify'
    if custom_logging is not None:
        logging.addLevelName(custom_logging, 'H_NOTIFY')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # file-logging
    log_file = 'h_notify.log'
    fh = logging.FileHandler(log_file)
    if level is None:
        level = file_log_err_level
    fh.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


class MarkdownNotifier(Notifier):
    def __init__(self, *args, folder=None, file_name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder = folder or ""
        self.file_name = file_name
        self.logger = init_logger(name='h_notify.MarkdownNotifier')

    def notify(self, anno=None, groupname=None, folder=None):
        try:
            vars = self.make_vars(anno, groupname)
            dt = dateutil.parser.parse(anno.updated)
            if not self.file_name:
                self.file_name = dt.strftime(date_format)
            file_path = os.path.join(self.folder, self.file_name)
            self.generate_markdown(
                file_path,
                anno.uri,
                vars["anno_url"],
                anno.doc_title,
                vars["quote"],
                anno.text,
                vars["tags"],
                dt,
            )
        except:
            self.logger.exception(f'Failed on id: {anno.id}, target: {anno.uri}')

    def write_markdown(self, md_object):
        file_name = md_object.file_name
        if not file_name.endswith(".md"):
            file_name += ".md"
        with open(file_name, "a+", encoding="utf-8") as file_object:
            text = (# we omit title and table of contents (empty anyway)
                md_object.file_data_text
                + md_object.reference.get_references_as_markdown()
            )
            file_object.write(text)

    def generate_markdown(
        self, file_path, source, location, topic, quote, note, tags, timestamp
    ):
        mdFile = MdUtils(file_path, title="")
        mdFile.new_header(
            level=2, title=f"{topic}", style="atx", add_table_of_contents="n"
        )
        if tags:
            tags = ' '.join(['#'+tag.strip() for tag in tags.split(',')])
            mdFile.new_line(f"{tags}")
        mdFile.new_paragraph(f"> {quote}")
        mdFile.new_line(f"> [{timestamp}]({location})")
        if note:
            mdFile.new_paragraph("Notes:", bold_italics_code="bi")
            mdFile.new_paragraph(note)
        mdFile.new_paragraph(f"[source]({source})")
        mdFile.new_paragraph("\n---\n")
        self.write_markdown(mdFile)


# Local markdown recipes


def notify_markdown_group_activity(
    group=None,
    groupname=None,
    token=None,
    folder=None,
    file_name=None,
    pickle=None,
    notified_ids=None,
):
    notifier = MarkdownNotifier(
        type="set",
        token=token,
        folder=folder,
        file_name=file_name,
        pickle=pickle,
        notified_ids=notified_ids,
    )
    notifier.notify_facet(facet="group", value=group, groupname=groupname)
    return notified_ids