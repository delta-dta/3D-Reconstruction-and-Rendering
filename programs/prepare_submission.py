"""Refresh submission metadata and entry pages without rerunning experiments."""

from finalize_course import ROOT, collect, course_averages, dashboard, object_pages, read, readme, write_json, write_progress


def main():
    summary = read(ROOT / 'results/course_summary.json')
    summary['findings']['novel_height_mean_fg_db'] = {
        int(height): value for height, value in summary['findings']['novel_height_mean_fg_db'].items()
    }
    rows = read(ROOT / 'results/metrics.json')
    objects, _ = collect(read(ROOT / 'configs/hw2_course.json'))
    averages = course_averages(rows)
    readme(rows, averages)
    dashboard(objects, rows, summary['findings'])
    object_pages(objects)
    summary['submission'] = read(ROOT / 'configs/submission.json')
    write_json(ROOT / 'results/course_summary.json', summary)
    write_progress()
    print('Updated group information, report overview, README and result dashboard.')


if __name__ == '__main__':
    main()
