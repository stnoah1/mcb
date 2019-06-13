function render_SHREC(input_dir, output_dir )
% subset = 'train_normal'

fig = figure('Visible','off');

if nargin < 2
  reverse_flg = false
end

dirpath = input_dir
imdirpath = output_dir
mkdir(imdirpath)
files = dir(dirpath)

inds = 3:length(files);

for i=inds
  modelname = files(i).name
  modelname_ = strsplit(modelname,'.');
  imname = modelname_{1};
  if exist([imdirpath '/' imname '.png']) > 0
    continue
  end
  try
    tic
      mesh = loadMesh([dirpath '/' modelname]);
      ims = render_views(mesh, 'use_dodecahedron_views', true, 'figHandle', fig, 'az', [0 90 180 270 0 0], 'el', [20 20 20 20 -80 110]);
    toc
    tic
        imwrite([ims{1} ims{2} ims{5} ; ims{3} ims{4} ims{6}], [imdirpath '/' imname '.png']);
      end
    toc
  end
end
