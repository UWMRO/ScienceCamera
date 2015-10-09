/// Andor Techonology Linux PCI Driver
/// Only the Driver is covered by the GPL.
/// Andor Technology SDK is not covered.
/// Copyright (C) Andor Technology

/// This program is free software; you can redistribute it and/or
/// modify it under the terms of the GNU General Public License
/// as published by the Free Software Foundation; either version 2
/// of the License, or (at your option) any later version.

/// This program is distributed in the hope that it will be useful,
/// but WITHOUT ANY WARRANTY; without even the implied warranty of
/// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
/// GNU General Public License for more details.

/// You should have received a copy of the GNU General Public License
/// along with this program; if not, write to the Free Software
/// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

int AndorPldMailboxRead(int iCardNo, ulong ulArg, ulong *pulData);
int AndorPldMailboxWrite(int iCardNo, ulong ulArg, ulong *pulData);
int AndorPldOpregRead(int iCardNo, ulong ulArg, ulong *pulData);
int AndorPldOpregWrite(int iCardNo, ulong ulArg, ulong *pulData);
int AndorPldConfigRead(int iCardNo, ulong ulArg, ulong *pulData);
int AndorPldConfigWrite(int iCardNo, ulong ulArg, ulong *pulData);

