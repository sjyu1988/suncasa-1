# import os
# import matplotlib as mpl
import matplotlib.pyplot as plt
# import matplotlib.colorbar as colorbar
# import sunpy.cm.cm as cm  ## to bootstrap sdoaia color map
# import matplotlib.cm as cm
# import matplotlib.colors as colors
import astropy.units as u
# from astropy.io import fits
# import matplotlib.dates as mdates
# from astropy.time import Time
from sunpy import map as smap
# import matplotlib.gridspec as gridspec
# import numpy.ma as ma
# import matplotlib.patches as patches
# from suncasa.utils import stackplot as stp
# from IPython import embed
# from astropy.coordinates import SkyCoord
import numpy as np
# from suncasa.utils import DButil
import warnings


class Sunmap(smap.GenericMap):

    def __init__(self, sunmap):
        self.sunmap = sunmap

    def map2wcsgrids(self, sunpymap=None, cell=False, antialiased=True):
        '''

        :param sunpymap:
        :param cell: if True, return the coordinates of the pixel centers. if False, return the coordinates of the pixel boundaries
        :return:
        '''
        # embed()
        import astropy.units as u
        if sunpymap is None:
            sunpymap = self.sunmap
        if cell:
            ny, nx = sunpymap.data.shape
            offset = 0.5
        else:
            ny, nx = sunpymap.data.shape
            offset = 0.0
        if antialiased:
            XX, YY = np.array([0, nx - 1]) + offset, np.array([0, ny - 1]) + offset
            mesh = sunpymap.pixel_to_world(XX * u.pix, YY * u.pix)
            mapx, mapy = np.linspace(mesh[0].Tx.value, mesh[-1].Tx.value, nx), np.linspace(mesh[0].Ty.value,
                                                                                           mesh[-1].Ty.value, ny)
            mapx = np.tile(mapx, ny).reshape(ny, nx)
            mapy = np.tile(mapy, nx).reshape(nx, ny).transpose()
        else:
            XX, YY = np.meshgrid(np.arange(nx) + offset, np.arange(ny) + offset)
            mesh = sunpymap.pixel_to_world(XX * u.pix, YY * u.pix)
            mapx, mapy = mesh.Tx.value, mesh.Ty.value
        return mapx, mapy

    def get_map_extent(self, sunpymap=None, rot=0):
        if sunpymap is None:
            sunpymap = self.sunmap
        rot = rot % 360
        if rot == 90:
            extent = np.array(
                sunpymap.yrange.to(u.arcsec).value[::-1].tolist() + sunpymap.xrange.to(u.arcsec).value.tolist())
            extent = extent - np.array([sunpymap.scale.axis2.value] * 2 + [sunpymap.scale.axis1.value] * 2) / 2.0
        elif rot == 180:
            extent = np.array(
                sunpymap.xrange.to(u.arcsec).value[::-1].tolist() + sunpymap.yrange.to(u.arcsec).value[::-1].tolist())
            extent = extent - np.array([sunpymap.scale.axis1.value] * 2 + [sunpymap.scale.axis2.value] * 2) / 2.0
        elif rot == 270:
            extent = np.array(
                sunpymap.yrange.to(u.arcsec).value.tolist() + sunpymap.xrange.to(u.arcsec).value[::-1].tolist())
            extent = extent - np.array([sunpymap.scale.axis1.value] * 2 + [sunpymap.scale.axis2.value] * 2) / 2.0
        else:
            extent = np.array(sunpymap.xrange.to(u.arcsec).value.tolist() + sunpymap.yrange.to(u.arcsec).value.tolist())
            extent = extent - np.array([sunpymap.scale.axis1.value] * 2 + [sunpymap.scale.axis2.value] * 2) / 2.0
        return extent

    def imshow(self, axes=None, rot=0, **kwargs):
        '''
        :param sunpymap:
        :param axes:
        :param rot: rotation angle in degrees counter-clockwise. Must be an integer multiple of 90.
        :param kwargs:
        :return:
        '''
        sunpymap = self.sunmap
        if axes is None:
            axes = plt.subplot()
        rot = rot % 360
        if rot == 0:
            imdata = sunpymap.data
        elif rot == 90:
            imdata = sunpymap.data.transpose()[:, ::-1]
        elif rot == 180:
            imdata = sunpymap.data[::-1, ::-1]
        elif rot == 270:
            imdata = sunpymap.data.transpose()[::-1, :]
        else:
            warnings.warn('rot must be an integer multiple of 90. rot not implemented!')
            imdata = sunpymap.data
            rot = 0
        extent = self.get_map_extent(rot=rot)
        im = axes.imshow(imdata, extent=extent, origin='lower', **kwargs)
        if rot == 0:
            axes.set_xlabel('Solar X [arcsec]')
            axes.set_ylabel('Solar Y [arcsec]')
        elif rot == 90:
            axes.set_xlabel('-Solar Y [arcsec]')
            axes.set_ylabel('Solar X [arcsec]')
        elif rot == 180:
            axes.set_xlabel('-Solar X [arcsec]')
            axes.set_ylabel('-Solar Y [arcsec]')
        elif rot == 270:
            axes.set_xlabel('Solar Y [arcsec]')
            axes.set_ylabel('-Solar X [arcsec]')
        return im

    def contour(self, axes=None, rot=0, **kwargs):
        sunpymap = self.sunmap
        if axes is None:
            axes = plt.subplot()
        rot = rot % 360
        if rot == 0:
            mapx, mapy = self.map2wcsgrids(cell=False)
        elif rot == 90:
            mapy, mapx = self.map2wcsgrids(cell=False)
        elif rot == 180:
            mapx, mapy = self.map2wcsgrids(cell=False)
        elif rot == 270:
            mapy, mapx = self.map2wcsgrids(cell=False)
        im = axes.contour(mapx, mapy, sunpymap.data, **kwargs)

        extent = self.get_map_extent(rot=rot)
        axes.set_xlim(extent[:2])
        axes.set_ylim(extent[2:])

        return im

    def draw_limb(self, axes=None, **kwargs):
        if 'c' not in kwargs and 'color' not in kwargs:
            kwargs['c'] = 'w'
        if 'ls' not in kwargs and 'linestyle' not in kwargs:
            kwargs['ls'] = '-'
        sunpymap = self.sunmap
        if axes is None:
            axes = plt.gca()
        axes.set_autoscale_on(False)
        rsun = sunpymap.rsun_obs
        phi = np.linspace(-180, 180, num=181) * u.deg
        x = np.cos(phi) * rsun
        y = np.sin(phi) * rsun
        im = axes.plot(x, y, **kwargs)
        return im

    def draw_grid(self, axes=None, grid_spacing=None, **kwargs):
        sunpymap = self.sunmap
        if grid_spacing is None:
            grid_spacing = 15 * u.deg

        def hgs2hcc(rsun, lon, lat, B0, L0):
            lon_L0 = lon - L0
            x = rsun * np.cos(lat) * np.sin(lon)
            y = rsun * (np.sin(lat) * np.cos(B0) - np.cos(lat) * np.cos(lon_L0) * np.sin(B0))
            z = rsun * (np.sin(lat) * np.sin(B0) + np.cos(lat) * np.cos(lon_L0) * np.cos(B0))
            return x, y, z

        def hcc2hpc(x, y, z, dsun):
            d = np.sqrt(x ** 2 + y ** 2 + (dsun - z) ** 2)
            Tx = np.arctan2(x, dsun - z)
            Ty = np.arcsin(y / d)
            return Tx, Ty

        if 'c' not in kwargs and 'color' not in kwargs:
            kwargs['c'] = 'w'
        if 'ls' not in kwargs and 'linestyle' not in kwargs:
            kwargs['ls'] = ':'
        dsun = sunpymap.dsun
        rsun = sunpymap.rsun_meters
        if axes is None:
            axes = plt.gca()
        im = []
        b0 = sunpymap.heliographic_latitude.to(u.deg)
        l0 = sunpymap.heliographic_longitude.to(u.deg)
        hg_longitude_deg = np.linspace(-90, 90, num=91) * u.deg
        hg_latitude_deg = np.arange(0, 90, grid_spacing.to(u.deg).value)
        hg_latitude_deg = np.hstack([-hg_latitude_deg[1:][::-1], hg_latitude_deg]) * u.deg
        for lat in hg_latitude_deg:
            c = hgs2hcc(rsun, hg_longitude_deg, lat * np.ones(91), b0, l0)
            coords = hcc2hpc(c[0], c[1], c[2], dsun)
            im += axes.plot(coords[0].to(u.arcsec), coords[1].to(u.arcsec), **kwargs)

        hg_longitude_deg = np.arange(0, 90, grid_spacing.to(u.deg).value)
        hg_longitude_deg = np.hstack([-hg_longitude_deg[1:][::-1], hg_longitude_deg]) * u.deg
        hg_latitude_deg = np.linspace(-90, 90, num=91) * u.deg

        for lon in hg_longitude_deg:
            c = hgs2hcc(rsun, lon * np.ones(91), hg_latitude_deg, b0, l0)
            coords = hcc2hpc(c[0], c[1], c[2], dsun)
            im += axes.plot(coords[0].to(u.arcsec), coords[1].to(u.arcsec), **kwargs)


    def imshow_RGB(self, maps, axes=None, returndataonly=False):
        from scipy import ndimage
        from astropy.coordinates import SkyCoord
        mapR = maps[0]
        znewR = mapR.data
        aiamapx, aiamapy = self.map2wcsgrids(sunpymap=mapR, cell=False, antialiased=False)
        mapG = maps[1]
        XX, YY = mapG.data_to_pixel(SkyCoord(aiamapx * u.arcsec, aiamapy * u.arcsec, frame=mapG.coordinate_frame))
        znewG = ndimage.map_coordinates(mapG.data, [YY, XX], order=1)
        mapB = maps[2]
        XX, YY = mapB.data_to_pixel(SkyCoord(aiamapx * u.arcsec, aiamapy * u.arcsec, frame=mapB.coordinate_frame))
        znewB = ndimage.map_coordinates(mapB.data, [YY, XX], order=1)

        znewR = np.sqrt(znewR)
        znewG = np.sqrt(znewG)
        znewB = np.sqrt(znewB)

        vmax, vmin = np.sqrt(5000), np.sqrt(10)
        # clrange=DButil.sdo_aia_scale_dict(304)
        znewR[znewR > vmax] = vmax
        znewR[znewR < vmin] = vmin
        # clrange=DButil.sdo_aia_scale_dict(94)
        vmax, vmin = np.sqrt(20000), np.sqrt(200)
        znewG[znewG > vmax] = vmax
        znewG[znewG < vmin] = vmin
        # clrange=DButil.sdo_aia_scale_dict(211)
        vmax, vmin = np.sqrt(5000), np.sqrt(100)
        znewB[znewB > vmax] = vmax
        znewB[znewB < vmin] = vmin
        znewR = (znewR - np.nanmin(znewR)) / (np.nanmax(znewR) - np.nanmin(znewR))
        znewG = (znewG - np.nanmin(znewG)) / (np.nanmax(znewG) - np.nanmin(znewG))
        znewB = (znewB - np.nanmin(znewB)) / (np.nanmax(znewB) - np.nanmin(znewB))
        # znew1 = np.sqrt(znew1)
        # znew2 = np.sqrt(znew2)
        # imshow(np.sqrt(np.stack([znew0, znew1, znew2], axis=-1)), extent=list(aiamap.xrange.value) + list(aiamap.yrange.value),origin='lower')
        if returndataonly:
            return np.stack([znewR, znewG, znewB], axis=-1)
        else:
            if axes:
                pass
            else:
                axes = plt.subplot()
            extent = self.get_map_extent(sunpymap=mapR)
            return axes.imshow(np.stack([znewR, znewG, znewB], axis=-1),
                               extent=extent, origin='lower')
