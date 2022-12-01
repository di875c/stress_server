import numpy as np


class BaseSquare:
    def __init__(self, x, y, div_x, div_y):
        self.x = x
        self.y = y
        self.area = x * y
        self.div_x = div_x
        self.div_y = div_y

    @property
    def cog(self):
        return self.x/2 + self.div_x, self.y/2 + self.div_y

    @property
    def inertia(self):
        return self.x * (self.y**3) / 12, self.y * (self.x**3) / 12


class AnySections:
    def __init__(self, *args, **kwargs):
        if 'square' in kwargs:
            self.squares = [BaseSquare(*_square) for _square in kwargs['square']]

    @property
    def area(self):
        return sum(_square.area for _square in self.squares)

    @property
    def cog(self):
        return tuple(
            sum(_square.area * _square.cog[_idx] for _square in self.squares) / self.area for _idx in range(2))

    @staticmethod
    def inertia_axis(_area=0, _mom_inertia=[], _div_x=0, _div_y=0, _cog=False, _alpha=0):
        #recalculation moment of inertia in another axis
        k = -1 if _cog else 1
        mom_inertia_x  = _mom_inertia[0] + k * _area * (_div_y ** 2)
        mom_inertia_y = _mom_inertia[1] + k * _area * (_div_x ** 2)
        mom_inertia_xy = _mom_inertia[2] + k * _area * (_div_x * _div_y)
        alpha = np.arctan(2 * mom_inertia_xy/(mom_inertia_x-mom_inertia_y)) / 2 if _cog else _alpha
        mom_inertia_max = mom_inertia_x * (np.cos(k*alpha)**2) + mom_inertia_y * (np.sin(k*alpha)**2) \
                         - mom_inertia_xy * np.sin(k*alpha*2)
        mom_inertia_min = mom_inertia_x * (np.sin(k*alpha)**2) + mom_inertia_y * (np.cos(k*alpha)**2) \
                         + mom_inertia_xy * np.sin(k*alpha*2)
        mom_inertia_0 = (mom_inertia_y - mom_inertia_x) * np.sin(alpha*2) / 2 \
                         + mom_inertia_xy * (np.cos(alpha)**2 - np.sin(alpha)**2)
        return mom_inertia_x, mom_inertia_y, mom_inertia_xy, alpha, mom_inertia_max, mom_inertia_min, mom_inertia_0

    @property
    def inertia(self):
        _inertia_list = list(sum(_square.inertia[_idx] + _square.area * (_square.cog[1-_idx]**2)
                                 for _square in self.squares) for _idx in range(2)) #Ix and Iy
        _inertia_list.append(sum(_square.area * _square.cog[0] * _square.cog[1] for _square in self.squares)) # append Ixy
        _inertia_list += self.inertia_axis(_area=self.area,
                                           _mom_inertia=_inertia_list,
                                           _div_x=self.cog[0],
                                           _div_y=self.cog[1],
                                           _cog=True)
        return dict(zip(('Ixx', 'Iyy', 'Ixy', 'Ixx_cog', 'Iyy_cog', 'Ixy_cog', 'alpha', 'Imax_princ', 'Imin_princ'), _inertia_list))


class AngleSection(AnySections):
    def __init__(self, height, width, th_1, th_2):
        self.height = height
        self.width = width
        self.th_h = th_1
        self.th_w = th_2
        super().__init__(square=[(th_1, height, 0, 0), (width - th_1, th_2, th_1, 0)])


class CSection(AnySections):
    def __init__(self, width1, height, width2, th_1, th_2, th_3):
        super().__init__(square=[(width1, th_1, 0, height-th_1), # upper flange
                                 (th_2, height - th_1 - th_3, 0, th_3), # web
                                 (width2, th_3, 0, 0)  # lower flange
                                 ])