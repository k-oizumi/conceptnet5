from __future__ import print_function
from conceptnet5.formats.sql import EdgeIndexWriter
from conceptnet5.formats.msgpack_stream import read_msgpack_stream
import os
import sys


def index_assertions(input_dir, output_db, shards=8, inputs=20):
    for writer_index in range(shards):
        print("Writing shard #%d" % writer_index)
        dbname = '%s.%d' % (output_db, writer_index)
        writer = EdgeIndexWriter(dbname, writer_index, shards,
                                 clear=True, allow_apsw=True)
        for filenum in range(inputs):
            filename = 'part_%02d.msgpack' % filenum
            path = os.path.join(input_dir, filename)
            print("\tIndexing %s" % filename, end='')
            sys.stdout.flush()
            count = 0
            with writer.transaction():
                for assertion, offset in read_msgpack_stream(path, offsets=True):
                    writer.add(assertion, filenum, offset)
                    count += 1
                    if count % 10000 == 0:
                        print('.', end='')
                        sys.stdout.flush()
            print()
        writer.close()


handle_file = index_assertions

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', help='directory of assertion files')
    parser.add_argument('output_db', help='SQLite file to output to')
    args = parser.parse_args()
    index_assertions(args.input_dir, args.output_db)
