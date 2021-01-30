import os, sys
sys.path.append("./hypothesis") # make submodule "visible"
from collections import defaultdict
import dateutil.parser
import logging
from mdutils.mdutils import MdUtils
from h_notify import Notifier

# file-logging
log_file = 'h_notify.log'
file_date_format = "%Y-%m-%d"
note_date_format = "%d-%m-%Y %H:%M"
file_log_err_level = logging.ERROR # logging.ERROR is recommended


def init_logger(name=None, level=None, custom_logging=None):
    logger_name = name or 'h_notify'
    if custom_logging is not None:
        logging.addLevelName(custom_logging, 'H_NOTIFY')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
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

    def notify(self, anno_list, groupname=None, folder=None):
        notes = defaultdict(lambda: defaultdict(list))
        for anno in anno_list:
            vars = self.make_vars(anno, groupname)
            dt = dateutil.parser.parse(anno.updated)
            if not self.file_name:
                self.file_name = dt.strftime(file_date_format)
            file_path = os.path.join(self.folder, self.file_name)
            note = notes[(file_path, anno.doc_title)]
            note["source"].append(anno.uri)
            note["location"].append(vars["anno_url"])
            note["note"].append(anno.text)
            note["quote"].append(vars["quote"])
            note["tags"].append(vars["tags"])
            note["timestamp"].append(dt.strftime(note_date_format))
        self.generate_markdown(notes)

    def generate_markdown(self, notes):
        for (file_path, title), body in notes.items():
            mdFile = MdUtils(file_path, title="")
            mdFile.new_header(
                level=1, title=title, style="atx", add_table_of_contents="n"
            )
            self.markdown_from_dict(mdFile, body)
            mdFile.new_paragraph("\n---\n")
            self.write_markdown(mdFile)

    def markdown_from_dict(self, mdFile, body):
        head_source = body['source'][0]
        mdFile.new_line(f"[source]({head_source})")

        for i, source in enumerate(body['source']):
            tags = body['tags'][i]
            note = body['note'][i]
            quote = body['quote'][i]
            location = body['location'][i]
            timestamp = body['timestamp'][i]

            if source != head_source:
                mdFile.new_paragraph(f"[source]({source})")
            else:
                mdFile.new_paragraph("")
                
            if tags:
                tags = ' '.join([f'#{tag.strip()}' for tag in tags.split(',')])
                mdFile.new_line(tags)
            
            indent = ''
            if note:
                note = "\n".join([
                    f"- {line}" if not line.strip().startswith('- ') else line
                    for line in note.split('\n') if line.strip()
                ])
                mdFile.new_paragraph(note)
                indent = '\t'
            mdFile.new_line(f"{indent}> {quote}")
            mdFile.new_line(f"{indent}> [{timestamp}]({location})")

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
    notifier.notify_facet(facet="group", value=group, groupname=groupname, gather=True)
    return notified_ids