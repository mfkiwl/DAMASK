import pytest
import numpy as np

from damask import grid_filters

class TestGridFilters:
   
    def test_cell_coord0(self):
         size = np.random.random(3)
         grid = np.random.randint(8,32,(3))
         coord = grid_filters.cell_coord0(grid,size)
         assert np.allclose(coord[0,0,0],size/grid*.5) and coord.shape == tuple(grid[::-1]) + (3,)

    def test_node_coord0(self):
         size = np.random.random(3)
         grid = np.random.randint(8,32,(3))
         coord = grid_filters.node_coord0(grid,size)
         assert np.allclose(coord[-1,-1,-1],size) and coord.shape == tuple(grid[::-1]+1) + (3,)

    def test_coord0(self):
         size = np.random.random(3)
         grid = np.random.randint(8,32,(3))
         c = grid_filters.cell_coord0(grid+1,size+size/grid)
         n = grid_filters.node_coord0(grid,size) + size/grid*.5
         assert np.allclose(c,n)

    @pytest.mark.parametrize('mode',[('cell'),('node')])
    def test_grid_DNA(self,mode):
         """Ensure that xx_coord0_gridSizeOrigin is the inverse of xx_coord0."""
         grid   = np.random.randint(8,32,(3))
         size   = np.random.random(3)
         origin = np.random.random(3)
         coord0 = eval('grid_filters.{}_coord0(grid,size,origin)'.format(mode))                     # noqa
         _grid,_size,_origin = eval('grid_filters.{}_coord0_gridSizeOrigin(coord0.reshape((-1,3)))'.format(mode))
         assert np.allclose(grid,_grid) and np.allclose(size,_size) and np.allclose(origin,_origin)

    def test_displacement_fluct_equivalence(self):
         """Ensure that fluctuations are periodic."""
         size = np.random.random(3)
         grid = np.random.randint(8,32,(3))
         F    = np.random.random(tuple(grid)+(3,3))
         assert np.allclose(grid_filters.node_displacement_fluct(size,F),
                            grid_filters.cell_2_node(grid_filters.cell_displacement_fluct(size,F)))

    def test_interpolation_nonperiodic(self):
         size = np.random.random(3)
         grid = np.random.randint(8,32,(3))
         F    = np.random.random(tuple(grid)+(3,3))
         assert np.allclose(grid_filters.node_coord(size,F) [1:-1,1:-1,1:-1],grid_filters.cell_2_node(
                            grid_filters.cell_coord(size,F))[1:-1,1:-1,1:-1])

    @pytest.mark.parametrize('mode',[('cell'),('node')])
    def test_coord0_origin(self,mode):
         origin= np.random.random(3)
         size  = np.random.random(3)                                                                # noqa
         grid  = np.random.randint(8,32,(3))
         shifted   = eval('grid_filters.{}_coord0(grid,size,origin)'.format(mode))
         unshifted = eval('grid_filters.{}_coord0(grid,size)'.format(mode))
         if   mode == 'cell':
            assert  np.allclose(shifted,unshifted+np.broadcast_to(origin,tuple(grid[::-1])  +(3,)))
         elif mode == 'node':
            assert  np.allclose(shifted,unshifted+np.broadcast_to(origin,tuple(grid[::-1]+1)+(3,)))

    @pytest.mark.parametrize('mode',[('cell'),('node')])
    def test_displacement_avg_vanishes(self,mode):
         """Ensure that random fluctuations in F do not result in average displacement."""
         size = np.random.random(3)                                                                 # noqa
         grid = np.random.randint(8,32,(3))
         F    = np.random.random(tuple(grid)+(3,3))
         F   += np.eye(3) - np.average(F,axis=(0,1,2))
         assert np.allclose(eval('grid_filters.{}_displacement_avg(size,F)'.format(mode)),0.0)

    @pytest.mark.parametrize('mode',[('cell'),('node')])
    def test_displacement_fluct_vanishes(self,mode):
         """Ensure that constant F does not result in fluctuating displacement."""
         size = np.random.random(3)                                                                 # noqa
         grid = np.random.randint(8,32,(3))
         F    = np.broadcast_to(np.random.random((3,3)), tuple(grid)+(3,3))                         # noqa
         assert np.allclose(eval('grid_filters.{}_displacement_fluct(size,F)'.format(mode)),0.0)

    def test_regrid(self):
         size = np.random.random(3)
         grid = np.random.randint(8,32,(3))
         F    = np.broadcast_to(np.eye(3), tuple(grid[::-1])+(3,3))
         assert all(grid_filters.regrid(size,F,grid) == np.arange(grid.prod()))