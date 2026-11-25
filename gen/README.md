# gen

Skeleton files that Studio's asset packer fills to write C for a project, such as sprite planes, tile maps and string tables. Studio ships them in the `reel` package.

## What lives here

Nothing yet. The skeletons come with the asset packer in plan milestone S6.

Every file the packer writes from a skeleton starts with an MIT SPDX line, so generated code carries its licence.

## What must never live here

- Any file under a licence other than MIT.
- Code that Studio itself runs. The packer lives in Studio's repository. Only the text it copies into a project lives here.
