#!/usr/bin/env python
###############################################################################
# $Id$
#
# Project:  GDAL/OGR Test Suite
# Purpose:  Test Raster Matrix Format used in GISes "Panorama"/"Integratsia".
# Author:   Andrey Kiselev <dron@ak4719.spb.edu>
#
###############################################################################
# Copyright (c) 2008, Andrey Kiselev <dron@ak4719.spb.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
###############################################################################

import os
import sys


import gdaltest
from osgeo import gdal
from osgeo import osr

###############################################################################
# Perform simple read tests.


def test_rmf_1():

    tst = gdaltest.GDALTest('rmf', 'byte.rsw', 1, 4672)
    return tst.testOpen(check_gt=(440720, 60, 0, 3751320, 0, -60))


def test_rmf_2():

    tst = gdaltest.GDALTest('rmf', 'byte-lzw.rsw', 1, 40503)
    with gdaltest.error_handler():
        return tst.testOpen()


def test_rmf_3():

    tst = gdaltest.GDALTest('rmf', 'float64.mtw', 1, 4672)
    with gdaltest.error_handler():
        return tst.testOpen(check_gt=(440720, 60, 0, 3751320, 0, -60))


def test_rmf_4():

    tst = gdaltest.GDALTest('rmf', 'rgbsmall.rsw', 1, 21212)
    ret = tst.testOpen(check_gt=(-44.840320, 0.003432, 0,
                                 -22.932584, 0, -0.003432))

    tst = gdaltest.GDALTest('rmf', 'rgbsmall.rsw', 2, 21053)
    ret = tst.testOpen(check_gt=(-44.840320, 0.003432, 0,
                                 -22.932584, 0, -0.003432))

    tst = gdaltest.GDALTest('rmf', 'rgbsmall.rsw', 3, 21349)
    return tst.testOpen(check_gt=(-44.840320, 0.003432, 0,
                                  -22.932584, 0, -0.003432))


def test_rmf_5():

    tst = gdaltest.GDALTest('rmf', 'rgbsmall-lzw.rsw', 1, 40503)
    with gdaltest.error_handler():
        ret = tst.testOpen()

    
    tst = gdaltest.GDALTest('rmf', 'rgbsmall-lzw.rsw', 2, 41429)
    with gdaltest.error_handler():
        ret = tst.testOpen()

    
    tst = gdaltest.GDALTest('rmf', 'rgbsmall-lzw.rsw', 3, 40238)
    with gdaltest.error_handler():
        return tst.testOpen()


def test_rmf_6():

    tst = gdaltest.GDALTest('rmf', 'big-endian.rsw', 1, 7782)
    with gdaltest.error_handler():
        ret = tst.testOpen()
    
    tst = gdaltest.GDALTest('rmf', 'big-endian.rsw', 2, 8480)
    with gdaltest.error_handler():
        ret = tst.testOpen()
    
    tst = gdaltest.GDALTest('rmf', 'big-endian.rsw', 3, 4195)
    with gdaltest.error_handler():
        return tst.testOpen()

###############################################################################
# Create simple copy and check.


def test_rmf_7():

    tst = gdaltest.GDALTest('rmf', 'byte.rsw', 1, 4672)

    return tst.testCreateCopy(check_srs=1, check_gt=1, vsimem=1)


def test_rmf_8():

    tst = gdaltest.GDALTest('rmf', 'rgbsmall.rsw', 2, 21053)

    return tst.testCreateCopy(check_srs=1, check_gt=1)

###############################################################################
# Create RMFHUGE=YES


def test_rmf_9():

    tst = gdaltest.GDALTest('rmf', 'byte.rsw', 1, 4672, options=['RMFHUGE=YES'])

    return tst.testCreateCopy(check_srs=1, check_gt=1, vsimem=1)

###############################################################################
# Compressed DEM


def test_rmf_10():

    tst = gdaltest.GDALTest('rmf', 't100.mtw', 1, 6388)

    with gdaltest.error_handler():
        return tst.testOpen()

###############################################################################
# Overviews


def test_rmf_11():

    test_fn = '/vsigzip/data/overviews.rsw.gz'
    src_ds = gdal.Open(test_fn)

    if src_ds is None:
        gdaltest.post_reason('Failed to open test dataset.')
        return 'fail'

    band1 = src_ds.GetRasterBand(1)

    if band1.GetOverviewCount() != 3:
        gdaltest.post_reason('overviews is missing')
        return 'fail'

    ovr_n = (0, 1, 2)
    ovr_size = (256, 64, 16)
    ovr_checksum = (32756, 51233, 3192)

    for i in ovr_n:
        ovr_band = band1.GetOverview(i)
        if ovr_band.XSize != ovr_size[i] or ovr_band.YSize != ovr_size[i]:
            msg = 'overview wrong size: overview %d, size = %d * %d,' % \
                  (i, ovr_band.XSize, ovr_band.YSize)
            gdaltest.post_reason(msg)
            return 'fail'

        if ovr_band.Checksum() != ovr_checksum[i]:
            msg = 'overview wrong checksum: overview %d, checksum = %d,' % \
                  (i, ovr_band.Checksum())
            gdaltest.post_reason(msg)
            return 'fail'

    return 'success'

###############################################################################
# Check file open with cucled header offsets .


def test_rmf_12a():

    tst = gdaltest.GDALTest('rmf', 'cucled-1.rsw', 1, 4672)
    with gdaltest.error_handler():
        return tst.testOpen(check_gt=(440720, 60, 0, 3751320, 0, -60))

###############################################################################
# Check file open with cucled header offsets .


def test_rmf_12b():

    tst = gdaltest.GDALTest('rmf', 'cucled-2.rsw', 1, 4672)
    with gdaltest.error_handler():
        return tst.testOpen(check_gt=(440720, 60, 0, 3751320, 0, -60))

###############################################################################
# Check file open with invalid subheader marker.


def test_rmf_12c():

    tst = gdaltest.GDALTest('rmf', 'invalid-subheader.rsw', 1, 4672)
    with gdaltest.error_handler():
        return tst.testOpen(check_gt=(440720, 60, 0, 3751320, 0, -60))

###############################################################################
# Check file open with corrupted subheader.


def test_rmf_12d():

    tst = gdaltest.GDALTest('rmf', 'corrupted-subheader.rsw', 1, 4672)
    return tst.testOpen(check_gt=(440720, 60, 0, 3751320, 0, -60))

###############################################################################
# Build overviews and check


def rmf_build_ov(source, testid, options, ov_sizes, crs, reopen=False, pass_count=1):

    rmf_drv = gdal.GetDriverByName('RMF')
    if rmf_drv is None:
        gdaltest.post_reason('RMF driver not found.')
        return 'fail'

    src_ds = gdal.Open('data/' + source, gdal.GA_ReadOnly)

    if src_ds is None:
        gdaltest.post_reason('Failed to open test dataset.')
        return 'fail'

    test_ds_name = 'tmp/ov-' + testid + '.tst'
    src_ds = rmf_drv.CreateCopy(test_ds_name, src_ds, options=options)
    if src_ds is None:
        gdaltest.post_reason('Failed to create test dataset copy.')
        return 'fail'

    for _ in range(pass_count):
        if reopen:
            src_ds = None
            src_ds = gdal.Open(test_ds_name, gdal.GA_Update)

            if src_ds is None:
                gdaltest.post_reason('Failed to open test dataset.')
                return 'fail'

        reopen = True
        err = src_ds.BuildOverviews(overviewlist=[2, 4])
        if err != 0:
            gdaltest.post_reason('BuildOverviews reports an error')
            return 'fail'

        src_ds = None
        src_ds = gdal.Open(test_ds_name, gdal.GA_ReadOnly)

        for iBand in range(src_ds.RasterCount):
            band = src_ds.GetRasterBand(iBand + 1)

            if band.GetOverviewCount() != 2:
                gdaltest.post_reason('overviews missing')
                return 'fail'

            for iOverview in range(band.GetOverviewCount()):
                ovr_band = band.GetOverview(iOverview)
                if ovr_band.XSize != ov_sizes[iOverview][0] or \
                   ovr_band.YSize != ov_sizes[iOverview][1]:
                    msg = 'overview wrong size: band %d, overview %d, size = %d * %d,' % \
                          (iBand, iOverview, ovr_band.XSize, ovr_band.YSize)
                    gdaltest.post_reason(msg)
                    return 'fail'

                if ovr_band.Checksum() != crs[iOverview][iBand]:
                    msg = 'overview wrong checksum: band %d, overview %d, checksum = %d,' % \
                          (iBand, iOverview, ovr_band.Checksum())
                    gdaltest.post_reason(msg)
                    return 'fail'

    src_ds = None
    os.remove(test_ds_name)

    return 'success'

###############################################################################
# Build overviews on newly created RSW file


def test_rmf_13():
    return rmf_build_ov(source='byte.rsw',
                        testid='13',
                        options=['RMFHUGE=NO'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087, 1087, 1087], [328, 328, 328]],
                        reopen=False)

###############################################################################
# Build overviews on newly created huge RSW file


def test_rmf_14():
    return rmf_build_ov(source='byte.rsw',
                        testid='14',
                        options=['RMFHUGE=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087, 1087, 1087], [328, 328, 328]],
                        reopen=False)

###############################################################################
# Build overviews on closed and reopened RSW file


def test_rmf_15():
    return rmf_build_ov(source='byte.rsw',
                        testid='15',
                        options=['RMFHUGE=NO'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087, 1087, 1087], [328, 328, 328]],
                        reopen=True)

###############################################################################
# Build overviews on closed and reopened huge RSW file


def test_rmf_16():
    return rmf_build_ov(source='byte.rsw',
                        testid='16',
                        options=['RMFHUGE=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087, 1087, 1087], [328, 328, 328]],
                        reopen=True)

###############################################################################
# Build overviews on newly created MTW file


def test_rmf_17():
    return rmf_build_ov(source='float64.mtw',
                        testid='17',
                        options=['RMFHUGE=NO', 'MTW=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087, 1087, 1087], [328, 328, 328]],
                        reopen=False)

###############################################################################
# Build overviews on newly created MTW file


def test_rmf_18():
    return rmf_build_ov(source='float64.mtw',
                        testid='18',
                        options=['RMFHUGE=YES', 'MTW=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087], [328]],
                        reopen=False)

###############################################################################
# Build overviews on closed and reopened MTW file


def test_rmf_19():
    return rmf_build_ov(source='float64.mtw',
                        testid='19',
                        options=['RMFHUGE=NO', 'MTW=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087], [328]],
                        reopen=True)

###############################################################################
# Build overviews on closed and reopened huge MTW file


def test_rmf_20():
    return rmf_build_ov(source='float64.mtw',
                        testid='20',
                        options=['RMFHUGE=YES', 'MTW=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087], [328]],
                        reopen=True)

###############################################################################
# Recreate overviews on newly created MTW file


def test_rmf_21():
    return rmf_build_ov(source='float64.mtw',
                        testid='21',
                        options=['RMFHUGE=NO', 'MTW=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087], [328]],
                        reopen=False,
                        pass_count=2)

###############################################################################
# Recreate overviews on newly created huge MTW file


def test_rmf_22():
    return rmf_build_ov(source='float64.mtw',
                        testid='22',
                        options=['RMFHUGE=YES', 'MTW=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087], [328]],
                        reopen=False,
                        pass_count=2)


###############################################################################
# Recreate overviews on closed and reopened MTW file

def test_rmf_23():
    return rmf_build_ov(source='float64.mtw',
                        testid='23',
                        options=['RMFHUGE=NO', 'MTW=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087], [328]],
                        reopen=True,
                        pass_count=2)

###############################################################################
# Recreate overviews on closed and reopened huge MTW file


def test_rmf_24():
    return rmf_build_ov(source='float64.mtw',
                        testid='24',
                        options=['RMFHUGE=YES', 'MTW=YES'],
                        ov_sizes=[[10, 10], [5, 5]],
                        crs=[[1087], [328]],
                        reopen=True,
                        pass_count=2)

###############################################################################
# Nodata write test


def test_rmf_25():
    rmf_drv = gdal.GetDriverByName('RMF')
    if rmf_drv is None:
        gdaltest.post_reason('RMF driver not found.')
        return 'fail'

    src_ds = gdal.Open('data/byte.rsw', gdal.GA_ReadOnly)

    if src_ds is None:
        gdaltest.post_reason('Failed to open test dataset.')
        return 'fail'

    test_ds_name = 'tmp/nodata.rsw'
    test_ds = rmf_drv.CreateCopy(test_ds_name, src_ds)
    if test_ds is None:
        gdaltest.post_reason('Failed to create test dataset copy.')
        return 'fail'

    test_ds.GetRasterBand(1).SetNoDataValue(33)
    nd = test_ds.GetRasterBand(1).GetNoDataValue()
    if nd != 33:
        gdaltest.post_reason('Invalid NoData value after CreateCopy.')
        return 'fail'
    test_ds = None

    test_ds = gdal.Open(test_ds_name, gdal.GA_Update)
    if test_ds is None:
        gdaltest.post_reason('Failed to reopen test dataset.')
        return 'fail'
    nd = test_ds.GetRasterBand(1).GetNoDataValue()
    if nd != 33:
        gdaltest.post_reason('Invalid NoData value after dataset reopen.')
        return 'fail'
    test_ds.GetRasterBand(1).SetNoDataValue(55)
    test_ds = None

    test_ds = gdal.Open(test_ds_name, gdal.GA_ReadOnly)
    if test_ds is None:
        gdaltest.post_reason('Failed to reopen test dataset.')
        return 'fail'
    nd = test_ds.GetRasterBand(1).GetNoDataValue()
    if nd != 55:
        gdaltest.post_reason('Invalid NoData value after dataset update.')
        return 'fail'

    test_ds = None
    os.remove(test_ds_name)

    return 'success'
###############################################################################
# Unit write test


def test_rmf_26():
    rmf_drv = gdal.GetDriverByName('RMF')
    if rmf_drv is None:
        gdaltest.post_reason('RMF driver not found.')
        return 'fail'

    src_ds = gdal.Open('data/float64.mtw', gdal.GA_ReadOnly)

    if src_ds is None:
        gdaltest.post_reason('Failed to open test dataset.')
        return 'fail'

    test_ds_name = 'tmp/unit.mtw'
    test_ds = rmf_drv.CreateCopy(test_ds_name, src_ds, options=['MTW=YES'])
    if test_ds is None:
        gdaltest.post_reason('Failed to create test dataset copy.')
        return 'fail'

    test_ds.GetRasterBand(1).SetUnitType('cm')
    unittype = test_ds.GetRasterBand(1).GetUnitType()
    if unittype != 'cm':
        gdaltest.post_reason('Invalid UnitType after CreateCopy.')
        return 'fail'
    test_ds = None

    test_ds = gdal.Open(test_ds_name, gdal.GA_Update)
    if test_ds is None:
        gdaltest.post_reason('Failed to reopen test dataset.')
        return 'fail'
    unittype = test_ds.GetRasterBand(1).GetUnitType()
    if unittype != 'cm':
        gdaltest.post_reason('Invalid UnitType after dataset reopen.')
        return 'fail'
    test_ds.GetRasterBand(1).SetUnitType('mm')
    test_ds = None

    test_ds = gdal.Open(test_ds_name, gdal.GA_ReadOnly)
    if test_ds is None:
        gdaltest.post_reason('Failed to reopen test dataset.')
        return 'fail'
    unittype = test_ds.GetRasterBand(1).GetUnitType()
    if unittype != 'mm':
        gdaltest.post_reason('Invalid UnitType after dataset update.')
        return 'fail'

    test_ds.GetRasterBand(1).SetUnitType('ft')
    unittype = test_ds.GetRasterBand(1).GetUnitType()
    if unittype != 'mm':
        gdaltest.post_reason('Invalid UnitType after dataset update.')
        return 'fail'

    test_ds = None
    os.remove(test_ds_name)

    return 'success'

###############################################################################
# Test read JPEG compressed RMF dataset


def test_rmf_27():

    if gdal.GetDriverByName('JPEG') is None:
        return 'skip'

    cs1 = [50553, 27604, 36652] #
    cs2 = [51009, 27640, 37765] # osx, clang

    ds = gdal.Open('data/jpeg-in-rmf.rsw', gdal.GA_ReadOnly)
    if ds is None:
        gdaltest.post_reason('Failed to open test dataset.')
        return 'fail'

    md = ds.GetMetadata('IMAGE_STRUCTURE')
    if md['COMPRESSION'] != 'JPEG':
        gdaltest.post_reason('"COMPRESSION" value is "%s" but expected "JPEG"' %
                              md['COMPRESSION'])
        return 'fail'

    cs = [0, 0, 0]
    for iBand in range(ds.RasterCount):
        band = ds.GetRasterBand(iBand + 1)
        cs[iBand] = band.Checksum()

    if cs != cs1 and cs != cs2:
        gdaltest.post_reason('Invalid checksum %s expected %s or %s.' %
                             (str(cs), str(cs1), str(cs2)))
        return 'fail'

    return 'success'


###############################################################################
# Check compression metadata


def test_rmf_28a():

    ds = gdal.Open('data/byte-lzw.rsw', gdal.GA_ReadOnly)
    if ds is None:
        gdaltest.post_reason('Failed to open test dataset.')
        return 'fail'

    md = ds.GetMetadata('IMAGE_STRUCTURE')
    if md['COMPRESSION'] != 'LZW':
        gdaltest.post_reason('"COMPRESSION" value is "%s" but expected "LZW"' %
                              md['COMPRESSION'])
        return 'fail'

    return 'success'


def test_rmf_28b():

    ds = gdal.Open('data/t100.mtw', gdal.GA_ReadOnly)
    if ds is None:
        gdaltest.post_reason('Failed to open test dataset.')
        return 'fail'

    md = ds.GetMetadata('IMAGE_STRUCTURE')
    if md['COMPRESSION'] != 'RMF_DEM':
        gdaltest.post_reason('"COMPRESSION" value is "%s" but expected "RMF_DEM"' %
                              md['COMPRESSION'])
        return 'fail'

    return 'success'


###############################################################################
# Check EPSG code

def test_rmf_29():

    rmf_drv = gdal.GetDriverByName('RMF')
    if rmf_drv is None:
        gdaltest.post_reason('RMF driver not found.')
        return 'fail'

    ds = gdal.Open('data/byte.rsw', gdal.GA_ReadOnly)
    if ds is None:
        gdaltest.post_reason('Failed to open test dataset.')
        return 'fail'

    test_ds_name = 'tmp/epsg.rsw'
    test_ds = rmf_drv.CreateCopy(test_ds_name, ds)
    if test_ds is None:
        gdaltest.post_reason('Failed to create test dataset copy.')
        return 'fail'

    sr = osr.SpatialReference()
    sr.SetFromUserInput('EPSG:3388')
    test_ds.SetProjection(sr.ExportToWkt())
    test_ds = None;
    ds = None

    test_ds = gdal.Open(test_ds_name, gdal.GA_ReadOnly)
    if test_ds is None:
        gdaltest.post_reason('Failed to open test dataset.')
        return 'fail'

    wkt = test_ds.GetProjectionRef()
    sr = osr.SpatialReference()
    sr.SetFromUserInput(wkt)
    if str(sr.GetAuthorityCode(None)) != '3388':
        gdaltest.post_reason('EPSG code is %s expected 3388.' %
                             str(sr.GetAuthorityCode(None)))
        return 'fail'

    return 'success'


###############################################################################
# Check interleaved access

def test_rmf_30():

    ds_name = 'tmp/interleaved.tif'
    gdal.Translate(ds_name, 'data/rgbsmall-lzw.rsw',
                   format='GTiff')

    ds = gdal.Open(ds_name)
    if ds is None:
        gdaltest.post_reason('Can\'t open ' + ds_name)
        return 'fail'
    expected_cs = [40503, 41429, 40238]
    cs = [ds.GetRasterBand(1).Checksum(),
          ds.GetRasterBand(2).Checksum(),
          ds.GetRasterBand(3).Checksum()]
    if cs != expected_cs:
        gdaltest.post_reason('Invalid checksum %s expected %s.' %
                             (str(cs), str(expected_cs)))
        return 'fail'
    return 'success'


###############################################################################
# Check compressed write


def test_rmf_31a():

    tst = gdaltest.GDALTest('rmf', 'small_world.tif', 1,
                            30111, options=['COMPRESS=NONE'])

    return tst.testCreateCopy(check_minmax=0, check_srs=1, check_gt=1)


def test_rmf_31b():

    tst = gdaltest.GDALTest('rmf', 'small_world.tif', 1,
                            30111, options=['COMPRESS=LZW'])

    return tst.testCreateCopy(check_minmax=0, check_srs=1, check_gt=1)


def test_rmf_31c():

    ds_name = 'tmp/rmf_31c.rsw'
    gdal.Translate(ds_name, 'data/small_world.tif',
                   format='RMF', options='-co COMPRESS=JPEG')

    ds = gdal.Open(ds_name)
    if ds is None:
        gdaltest.post_reason('Can\'t open ' + ds_name)
        return 'fail'
    expected_cs1 = [25789, 27405, 31974]
    expected_cs2 = [23764, 25264, 33585] # osx
    cs = [ds.GetRasterBand(1).Checksum(),
          ds.GetRasterBand(2).Checksum(),
          ds.GetRasterBand(3).Checksum()]

    if cs != expected_cs1 and cs != expected_cs2:
        gdaltest.post_reason('Invalid checksum %s expected %s or %s.' %
                             (str(cs), str(expected_cs1), str(expected_cs2)))
        return 'fail'
    return 'success'


def test_rmf_31d():

    tst = gdaltest.GDALTest('rmf', 't100.mtw', 1,
                            6388, options=['MTW=YES', 'COMPRESS=RMF_DEM'])

    return tst.testCreateCopy(check_minmax=0, check_srs=1, check_gt=1)


def test_rmf_31e():
    try:
        import numpy
    except ImportError:
        return 'skip'

    drv = gdal.GetDriverByName('Gtiff')
    if drv is None:
        return 'skip'
    # Create test data
    stripeSize = 32;
    sx = 256
    sy = 8*stripeSize
    tst_name = 'tmp/rmf_31e.tif'
    tst_ds = drv.Create(tst_name, sx, sy, 1, gdal.GDT_Int32 )
    if tst_ds is None:
        gdaltest.post_reason('Can\'t create ' + tst_name)
        return 'fail'

    # No deltas
    buff = numpy.zeros((sx, stripeSize), dtype = numpy.int32)
    tst_ds.GetRasterBand(1).WriteArray(buff, 0, 0)

    # 4-bit deltas
    buff = numpy.random.randint(0, 16, [stripeSize, sx])
    tst_ds.GetRasterBand(1).WriteArray(buff, 0, stripeSize)

    # 8-bit deltas
    buff = numpy.random.randint(0, 256, [stripeSize, sx])
    tst_ds.GetRasterBand(1).WriteArray(buff, 0, stripeSize*2)

    # 12-bit deltas
    buff = numpy.random.randint(0, 256*16, [stripeSize, sx])
    tst_ds.GetRasterBand(1).WriteArray(buff, 0, stripeSize*3)

    # 16-bit deltas
    buff = numpy.random.randint(0, 256*256, [stripeSize, sx])
    tst_ds.GetRasterBand(1).WriteArray(buff, 0, stripeSize*4)

    # 24-bit deltas
    buff = numpy.random.randint(0, 256*256*256, [stripeSize, sx])
    tst_ds.GetRasterBand(1).WriteArray(buff, 0, stripeSize*5)

    # 32-bit deltas
    buff = numpy.random.randint(0, 256*256*256*128 - 1, [stripeSize, sx])
    tst_ds.GetRasterBand(1).WriteArray(buff, 0, stripeSize*6)

    tst_ds = None
    tst_ds = gdal.Open(tst_name)
    if tst_ds is None:
        gdaltest.post_reason('Can\'t open ' + tst_name)
        return 'fail'

    cs = tst_ds.GetRasterBand(1).Checksum()
    tst_ds = None

    tst = gdaltest.GDALTest('rmf', '../' + tst_name, 1,
                            cs, options=['MTW=YES', 'COMPRESS=RMF_DEM'])

    return tst.testCreateCopy(check_minmax=0, check_srs=1, check_gt=1)


###############################################################################
# Check parallel compression

def test_rmf_32a():

    ds_name = 'tmp/rmf_32a.rsw'
    gdal.Translate(ds_name, 'data/small_world.tif', format='RMF',
                   options='-outsize 400% 400% -co COMPRESS=LZW -co NUM_THREADS=0')

    tst = gdaltest.GDALTest('rmf', '../' + ds_name, 1, 5540)
    res = tst.testOpen(check_gt=None)
    os.remove(ds_name)

    return res


def test_rmf_32b():

    ds_name = 'tmp/rmf_32b.rsw'
    gdal.Translate(ds_name, 'data/small_world.tif', format='RMF',
                   options='-outsize 400% 400% -co COMPRESS=LZW -co NUM_THREADS=4')

    tst = gdaltest.GDALTest('rmf', '../' + ds_name, 1, 5540)
    res = tst.testOpen(check_gt=None)
    os.remove(ds_name)

    return res


###############################################################################
# Parallel build overviews on newly created RSW file


def test_rmf_32c():
    ds_name = 'tmp/rmf_32c.rsw'
    gdal.Translate(ds_name, 'data/small_world.tif', format='RMF',
                   options='-outsize 400% 400% -co COMPRESS=LZW -co NUM_THREADS=4')

    res = rmf_build_ov(source='../' + ds_name,
                       testid='32c',
                       options=['RMFHUGE=NO', 'COMPRESS=LZW', 'NUM_THREADS=4'],
                       ov_sizes=[[800, 400], [400, 200]],
                       crs=[[50261, 64846, 28175], [30111, 32302, 40026]],
                       reopen=False)
    os.remove(ds_name)

    return res


###############################################################################
# Read 1-bit & 4-bit files


def test_rmf_33a():

    tst = gdaltest.GDALTest('rmf', '1bit.rsw', 1, 34325)
    return tst.testOpen()


def test_rmf_33b():

    tst = gdaltest.GDALTest('rmf', '4bit.rsw', 1, 55221)
    return tst.testOpen()


def test_rmf_33c():

    tst = gdaltest.GDALTest('rmf', '4bit-lzw.rsw', 1, 55221)
    return tst.testOpen()


###############################################################################


gdaltest_list = [
    test_rmf_1,
    test_rmf_2,
    test_rmf_3,
    test_rmf_4,
    test_rmf_5,
    test_rmf_6,
    test_rmf_7,
    test_rmf_8,
    test_rmf_9,
    test_rmf_10,
    test_rmf_11,
    test_rmf_12a,
    test_rmf_12b,
    test_rmf_12c,
    test_rmf_12d,
    test_rmf_13,
    test_rmf_14,
    test_rmf_15,
    test_rmf_16,
    test_rmf_17,
    test_rmf_18,
    test_rmf_19,
    test_rmf_20,
    test_rmf_21,
    test_rmf_22,
    test_rmf_23,
    test_rmf_24,
    test_rmf_25,
    test_rmf_26,
    test_rmf_27,
    test_rmf_28a,
    test_rmf_28b,
    test_rmf_29,
    test_rmf_30,
    test_rmf_31a,
    test_rmf_31b,
    test_rmf_31c,
    test_rmf_31d,
    test_rmf_31e,
    test_rmf_32a,
    test_rmf_32b,
    test_rmf_32c,
    test_rmf_33a,
    test_rmf_33b,
    test_rmf_33c,
]

if __name__ == '__main__':

    gdaltest.setup_run('rmf')

    gdaltest.run_tests(gdaltest_list)

    sys.exit(gdaltest.summarize())
